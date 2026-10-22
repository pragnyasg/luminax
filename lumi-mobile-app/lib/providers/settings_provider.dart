import 'package:flutter/foundation.dart';
import '../models/app_settings.dart';
import '../services/storage_service.dart';

class SettingsProvider with ChangeNotifier {
  final StorageService _storageService = StorageService();
  AppSettings _settings = const AppSettings();

  AppSettings get settings => _settings;
  bool get useMockMode => _settings.useMockMode;
  String get backendUrl => _settings.backendUrl;

  Future<void> init() async {
    _settings = await _storageService.loadSettings();
    notifyListeners();
  }

  Future<void> updateSettings(AppSettings newSettings) async {
    _settings = newSettings;
    await _storageService.saveSettings(_settings);
    notifyListeners();
  }

  Future<void> setMockMode(bool enable) async {
    _settings = _settings.copyWith(useMockMode: enable);
    await _storageService.saveSettings(_settings);
    notifyListeners();
  }

  Future<void> setBackendUrl(String url) async {
    _settings = _settings.copyWith(backendUrl: url);
    await _storageService.saveSettings(_settings);
    notifyListeners();
  }
}
