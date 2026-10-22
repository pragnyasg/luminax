import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/robot_status.dart';
import '../models/battery_status.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';
import '../services/mock_data_service.dart';

class RobotProvider with ChangeNotifier {
  final ApiService _apiService;
  final WebSocketService _wsService;
  bool _useMockMode = false;

  RobotStatus _status = MockDataService.getMockRobotStatus();
  WsConnectionState _connectionState = WsConnectionState.disconnected;
  bool _isLoading = false;
  String? _errorMessage;

  StreamSubscription? _wsStatusSub;
  StreamSubscription? _wsConnSub;
  Timer? _pollingTimer;

  RobotStatus get status => _status;
  BatteryStatus get battery => _status.battery;
  Pose2D get location => _status.location;
  WsConnectionState get connectionState => _connectionState;
  bool get isConnected => _useMockMode ? true : (_connectionState == WsConnectionState.connected && _status.isConnected);
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  RobotProvider({
    required ApiService apiService,
    required WebSocketService wsService,
  })  : _apiService = apiService,
        _wsService = wsService {
    _initSubscriptions();
  }

  void updateConfig({required bool useMockMode, required String backendUrl}) {
    _useMockMode = useMockMode;
    _apiService.baseUrl = backendUrl;
    _wsService.updateBaseUrl(backendUrl);

    if (_useMockMode) {
      _status = MockDataService.getMockRobotStatus();
      _connectionState = WsConnectionState.connected;
      notifyListeners();
    } else {
      refreshStatus();
    }
  }

  void _initSubscriptions() {
    _wsConnSub = _wsService.connectionStateStream.listen((state) {
      if (!_useMockMode) {
        _connectionState = state;
        notifyListeners();
      }
    });

    _wsStatusSub = _wsService.robotStatusStream.listen((newStatus) {
      if (!_useMockMode) {
        _status = newStatus;
        notifyListeners();
      }
    });

    // Fallback polling every 5 seconds
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (!_useMockMode && _connectionState != WsConnectionState.connected) {
        refreshStatus();
      }
    });
  }

  Future<void> refreshStatus() async {
    if (_useMockMode) {
      _status = MockDataService.getMockRobotStatus();
      notifyListeners();
      return;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final fetched = await _apiService.fetchRobotStatus();
      _status = fetched;
      _connectionState = WsConnectionState.connected;
    } catch (e) {
      _errorMessage = e.toString();
      _connectionState = WsConnectionState.disconnected;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> sendManualControl(double linearX, double angularZ, {bool safetyOverride = false}) async {
    if (_useMockMode) return true;
    return await _apiService.sendManualControl(linearX, angularZ, safetyOverride: safetyOverride);
  }

  Future<bool> sendStop() async {
    if (_useMockMode) return true;
    return await _apiService.sendStop();
  }

  @override
  void dispose() {
    _wsStatusSub?.cancel();
    _wsConnSub?.cancel();
    _pollingTimer?.cancel();
    super.dispose();
  }
}
