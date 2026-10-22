import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/destination.dart';
import '../models/navigation_goal.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';
import '../services/mock_data_service.dart';

class NavigationProvider with ChangeNotifier {
  final ApiService _apiService;
  final WebSocketService _wsService;
  bool _useMockMode = false;

  List<Destination> _destinations = [];
  NavigationGoal? _currentGoal;
  bool _isLoading = false;
  String? _errorMessage;

  StreamSubscription? _wsNavSub;

  List<Destination> get destinations => _destinations;
  NavigationGoal? get currentGoal => _currentGoal;
  bool get isNavigating => _currentGoal != null && _currentGoal!.status == 'EXECUTING';
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  NavigationProvider({
    required ApiService apiService,
    required WebSocketService wsService,
  })  : _apiService = apiService,
        _wsService = wsService {
    _wsNavSub = _wsService.navigationStream.listen((goal) {
      if (!_useMockMode) {
        _currentGoal = goal;
        notifyListeners();
      }
    });
  }

  void updateConfig({required bool useMockMode}) {
    _useMockMode = useMockMode;
    loadNavigationData();
  }

  Future<void> loadNavigationData() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    if (_useMockMode) {
      _destinations = MockDataService.getMockDestinations();
      _isLoading = false;
      notifyListeners();
      return;
    }

    try {
      final list = await _apiService.fetchDestinations();
      _destinations = list;
      final goal = await _apiService.fetchCurrentGoal();
      _currentGoal = goal;
    } catch (e) {
      _errorMessage = e.toString();
      _destinations = MockDataService.getMockDestinations();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> dispatchGoalToDestination(Destination dest) async {
    if (_useMockMode) {
      _currentGoal = NavigationGoal(
        goalId: 'nav-mock-${DateTime.now().millisecondsSinceEpoch}',
        destinationName: dest.name,
        targetX: dest.x,
        targetY: dest.y,
        status: 'EXECUTING',
        progressPercent: 15.0,
        distanceRemainingM: 2.4,
        estimatedSecondsRemaining: 7.0,
        createdAt: DateTime.now().toIso8601String(),
      );
      notifyListeners();
      return true;
    }

    try {
      final goal = await _apiService.dispatchGoal(destinationId: dest.id);
      _currentGoal = goal;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> dispatchGoalToCoordinates(double x, double y) async {
    if (_useMockMode) {
      _currentGoal = NavigationGoal(
        goalId: 'nav-mock-${DateTime.now().millisecondsSinceEpoch}',
        destinationName: 'Custom Target',
        targetX: x,
        targetY: y,
        status: 'EXECUTING',
        progressPercent: 5.0,
        distanceRemainingM: 3.0,
        estimatedSecondsRemaining: 8.5,
        createdAt: DateTime.now().toIso8601String(),
      );
      notifyListeners();
      return true;
    }

    try {
      final goal = await _apiService.dispatchGoal(x: x, y: y);
      _currentGoal = goal;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> cancelGoal() async {
    if (_useMockMode) {
      if (_currentGoal != null) {
        _currentGoal = NavigationGoal(
          goalId: _currentGoal!.goalId,
          destinationName: _currentGoal!.destinationName,
          targetX: _currentGoal!.targetX,
          targetY: _currentGoal!.targetY,
          status: 'CANCELED',
          progressPercent: _currentGoal!.progressPercent,
          distanceRemainingM: 0.0,
          estimatedSecondsRemaining: 0.0,
          createdAt: _currentGoal!.createdAt,
        );
        notifyListeners();
      }
      return true;
    }

    final success = await _apiService.cancelGoal();
    if (success) {
      loadNavigationData();
    }
    return success;
  }

  @override
  void dispose() {
    _wsNavSub?.cancel();
    super.dispose();
  }
}
