import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/robot_status.dart';
import '../models/emergency_event.dart';
import '../models/navigation_goal.dart';

enum WsConnectionState { disconnected, connecting, connected }

class WebSocketService {
  WebSocketChannel? _channel;
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  bool _isDisposed = false;
  int _reconnectAttempts = 0;

  String _baseUrl = 'http://192.168.1.100:8000';
  WsConnectionState _connectionState = WsConnectionState.disconnected;

  // Stream Controllers
  final _connectionStateController = StreamController<WsConnectionState>.broadcast();
  final _rawEventController = StreamController<Map<String, dynamic>>.broadcast();
  final _robotStatusController = StreamController<RobotStatus>.broadcast();
  final _emergencyController = StreamController<EmergencyEvent>.broadcast();
  final _navigationController = StreamController<NavigationGoal>.broadcast();

  Stream<WsConnectionState> get connectionStateStream => _connectionStateController.stream;
  Stream<Map<String, dynamic>> get rawEventStream => _rawEventController.stream;
  Stream<RobotStatus> get robotStatusStream => _robotStatusController.stream;
  Stream<EmergencyEvent> get emergencyStream => _emergencyController.stream;
  Stream<NavigationGoal> get navigationStream => _navigationController.stream;
  WsConnectionState get state => _connectionState;

  void updateBaseUrl(String url) {
    if (_baseUrl != url) {
      _baseUrl = url;
      disconnect();
      connect();
    }
  }

  void connect([String? url]) {
    if (url != null) _baseUrl = url;
    if (_isDisposed || _connectionState == WsConnectionState.connected) return;

    _setState(WsConnectionState.connecting);

    try {
      final wsUri = _getWsUri(_baseUrl);
      _channel = WebSocketChannel.connect(wsUri);

      _channel!.stream.listen(
        (data) {
          _onMessageReceived(data);
        },
        onDone: () {
          _onDisconnected();
        },
        onError: (err) {
          _onDisconnected();
        },
        cancelOnError: true,
      );

      _reconnectAttempts = 0;
      _setState(WsConnectionState.connected);
      _startPingTimer();
    } catch (e) {
      _onDisconnected();
    }
  }

  void _onMessageReceived(dynamic raw) {
    try {
      final Map<String, dynamic> msg = jsonDecode(raw.toString()) as Map<String, dynamic>;
      _rawEventController.add(msg);

      final String type = msg['type'] as String? ?? '';
      final dynamic data = msg['data'] ?? msg['event'];

      if (type == 'robot.status' && data is Map<String, dynamic>) {
        _robotStatusController.add(RobotStatus.fromJson(data));
      } else if (type == 'connection_established' && data is Map<String, dynamic>) {
        if (data['robot_status'] is Map<String, dynamic>) {
          _robotStatusController.add(RobotStatus.fromJson(data['robot_status']));
        }
      } else if ((type == 'vision.fall_detected' || type == 'emergency.created') && data is Map<String, dynamic>) {
        _emergencyController.add(EmergencyEvent.fromJson(data));
      } else if ((type == 'navigation.started' || type == 'navigation.feedback' || type == 'navigation.completed') && data is Map<String, dynamic>) {
        _navigationController.add(NavigationGoal.fromJson(data));
      }
    } catch (_) {}
  }

  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      if (_connectionState == WsConnectionState.connected && _channel != null) {
        try {
          _channel!.sink.add('ping');
        } catch (_) {}
      }
    });
  }

  void _onDisconnected() {
    _pingTimer?.cancel();
    _setState(WsConnectionState.disconnected);

    if (!_isDisposed) {
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    _reconnectAttempts++;
    final delaySeconds = (_reconnectAttempts * 2).clamp(2, 10);
    _reconnectTimer = Timer(Duration(seconds: delaySeconds), () {
      if (!_isDisposed && _connectionState == WsConnectionState.disconnected) {
        connect();
      }
    });
  }

  void disconnect() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
    _setState(WsConnectionState.disconnected);
  }

  void _setState(WsConnectionState s) {
    _connectionState = s;
    if (!_connectionStateController.isClosed) {
      _connectionStateController.add(s);
    }
  }

  Uri _getWsUri(String httpUrl) {
    final parsed = Uri.parse(httpUrl);
    final scheme = parsed.scheme == 'https' ? 'wss' : 'ws';
    return parsed.replace(scheme: scheme, path: '/api/v1/ws');
  }

  void dispose() {
    _isDisposed = true;
    disconnect();
    _connectionStateController.close();
    _rawEventController.close();
    _robotStatusController.close();
    _emergencyController.close();
    _navigationController.close();
  }
}
