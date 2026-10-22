import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/emergency_event.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';
import '../services/mock_data_service.dart';

class EmergencyProvider with ChangeNotifier {
  final ApiService _apiService;
  final WebSocketService _wsService;
  bool _useMockMode = false;

  List<EmergencyEvent> _emergencies = [];
  bool _isLoading = false;
  String? _errorMessage;

  StreamSubscription? _wsEmergencySub;

  List<EmergencyEvent> get emergencies => _emergencies;
  List<EmergencyEvent> get unacknowledged => _emergencies.where((e) => !e.acknowledged).toList();
  bool get hasActiveEmergency => unacknowledged.isNotEmpty;
  EmergencyEvent? get latestActiveEmergency => unacknowledged.isNotEmpty ? unacknowledged.first : null;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  EmergencyProvider({
    required ApiService apiService,
    required WebSocketService wsService,
  })  : _apiService = apiService,
        _wsService = wsService {
    _wsEmergencySub = _wsService.emergencyStream.listen((event) {
      // Check if already in list to avoid duplicates
      final index = _emergencies.indexWhere((e) => e.eventId == event.eventId);
      if (index >= 0) {
        _emergencies[index] = event;
      } else {
        _emergencies.insert(0, event);
      }
      notifyListeners();
    });
  }

  void updateConfig({required bool useMockMode}) {
    _useMockMode = useMockMode;
    loadEmergencies();
  }

  Future<void> loadEmergencies() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    if (_useMockMode) {
      _emergencies = MockDataService.getMockEmergencies();
      _isLoading = false;
      notifyListeners();
      return;
    }

    try {
      final list = await _apiService.fetchEmergencies();
      _emergencies = list;
    } catch (e) {
      _errorMessage = e.toString();
      _emergencies = MockDataService.getMockEmergencies();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> acknowledgeEmergency(String eventId, String acknowledgedBy, {String? note}) async {
    if (_useMockMode) {
      final index = _emergencies.indexWhere((e) => e.eventId == eventId);
      if (index >= 0) {
        final ev = _emergencies[index];
        _emergencies[index] = EmergencyEvent(
          eventId: ev.eventId,
          eventType: ev.eventType,
          severity: ev.severity,
          timestamp: ev.timestamp,
          confidence: ev.confidence,
          personName: ev.personName,
          posture: ev.posture,
          location: ev.location,
          snapshotUrl: ev.snapshotUrl,
          acknowledged: true,
          acknowledgedAt: DateTime.now().toIso8601String(),
          acknowledgedBy: acknowledgedBy,
          resolutionNotes: note,
        );
        notifyListeners();
      }
      return true;
    }

    final success = await _apiService.acknowledgeEmergency(eventId, acknowledgedBy, note: note);
    if (success) {
      loadEmergencies();
    }
    return success;
  }

  Future<bool> callResponder(String eventId, {String? phone}) async {
    if (_useMockMode) return true;
    return await _apiService.callEmergencyResponder(eventId, phone: phone);
  }

  Future<bool> simulateFall() async {
    if (_useMockMode) {
      final mockFall = EmergencyEvent(
        eventId: 'em-sim-${DateTime.now().millisecondsSinceEpoch}',
        eventType: 'fall_confirmed',
        severity: 'CRITICAL',
        timestamp: DateTime.now().toIso8601String(),
        confidence: 0.96,
        personName: 'Primary Patient',
        posture: 'lying_down',
        acknowledged: false,
      );
      _emergencies.insert(0, mockFall);
      notifyListeners();
      return true;
    }

    final ev = await _apiService.simulateFallAlert();
    if (ev != null) {
      _emergencies.insert(0, ev);
      notifyListeners();
      return true;
    }
    return false;
  }

  @override
  void dispose() {
    _wsEmergencySub?.cancel();
    super.dispose();
  }
}
