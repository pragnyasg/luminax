import 'package:flutter/foundation.dart';
import '../models/medicine.dart';
import '../services/api_service.dart';
import '../services/mock_data_service.dart';

class MedicineProvider with ChangeNotifier {
  final ApiService _apiService;
  bool _useMockMode = false;

  List<MedicineSchedule> _schedules = [];
  List<MedicineLogEntry> _logs = [];
  AdherenceSummary _adherence = const AdherenceSummary(totalDoses: 0, takenCount: 0, skippedCount: 0, missedCount: 0, adherenceRatePercent: 100.0);
  bool _isLoading = false;
  String? _errorMessage;

  List<MedicineSchedule> get schedules => _schedules;
  List<MedicineLogEntry> get logs => _logs;
  AdherenceSummary get adherence => _adherence;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  MedicineProvider({required ApiService apiService}) : _apiService = apiService;

  void updateConfig({required bool useMockMode}) {
    _useMockMode = useMockMode;
    loadMedicines();
  }

  Future<void> loadMedicines() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    if (_useMockMode) {
      _schedules = MockDataService.getMockMedicines();
      _logs = MockDataService.getMockMedicineLogs();
      _adherence = const AdherenceSummary(totalDoses: 10, takenCount: 9, skippedCount: 1, missedCount: 0, adherenceRatePercent: 90.0);
      _isLoading = false;
      notifyListeners();
      return;
    }

    try {
      final list = await _apiService.fetchMedicines();
      _schedules = list;
      final adh = await _apiService.fetchAdherenceSummary();
      _adherence = adh;
    } catch (e) {
      _errorMessage = e.toString();
      _schedules = MockDataService.getMockMedicines();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addMedicine({
    required String name,
    required String dosage,
    required String scheduledTime,
    required List<String> daysOfWeek,
    String? instructions,
  }) async {
    if (_useMockMode) {
      final newMed = MedicineSchedule(
        id: 'med-${DateTime.now().millisecondsSinceEpoch}',
        name: name,
        dosage: dosage,
        scheduledTime: scheduledTime,
        daysOfWeek: daysOfWeek,
        instructions: instructions,
        isActive: true,
        createdAt: DateTime.now().toIso8601String(),
      );
      _schedules.insert(0, newMed);
      notifyListeners();
      return true;
    }

    try {
      final created = await _apiService.createMedicine({
        'name': name,
        'dosage': dosage,
        'scheduled_time': scheduledTime,
        'days_of_week': daysOfWeek,
        'instructions': instructions,
      });
      _schedules.insert(0, created);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> deleteMedicine(String id) async {
    if (_useMockMode) {
      _schedules.removeWhere((s) => s.id == id);
      notifyListeners();
      return true;
    }

    final success = await _apiService.deleteMedicine(id);
    if (success) {
      _schedules.removeWhere((s) => s.id == id);
      notifyListeners();
    }
    return success;
  }

  Future<bool> triggerReminder(String id) async {
    if (_useMockMode) return true;
    return await _apiService.triggerMedicineReminder(id);
  }

  Future<bool> markAction(String id, String action, String confirmedBy) async {
    if (_useMockMode) {
      _logs.insert(0, MedicineLogEntry(
        id: 'log-${DateTime.now().millisecondsSinceEpoch}',
        medicineId: id,
        medicineName: _schedules.firstWhere((s) => s.id == id, orElse: () => _schedules.first).name,
        dosage: '1 dose',
        scheduledTime: 'Now',
        status: action,
        confirmedBy: confirmedBy,
        confirmedAt: 'Just now',
      ));
      notifyListeners();
      return true;
    }

    final success = await _apiService.recordMedicineAction(id, action, confirmedBy);
    if (success) {
      loadMedicines();
    }
    return success;
  }
}
