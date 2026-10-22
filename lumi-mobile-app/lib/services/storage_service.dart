import 'package:shared_preferences/shared_preferences.dart';
import '../models/app_settings.dart';

class StorageService {
  static const _keyBackendUrl = 'lumi_backend_url';
  static const _keyApiKey = 'lumi_api_key';
  static const _keyMockMode = 'lumi_mock_mode';
  static const _keyCaregiverName = 'lumi_caregiver_name';
  static const _keyCaregiverPhone = 'lumi_caregiver_phone';

  Future<AppSettings> loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return AppSettings(
        backendUrl: prefs.getString(_keyBackendUrl) ?? 'http://192.168.1.100:8000',
        apiKey: prefs.getString(_keyApiKey),
        useMockMode: prefs.getBool(_keyMockMode) ?? false,
        caregiverName: prefs.getString(_keyCaregiverName) ?? 'Primary Caregiver',
        caregiverPhone: prefs.getString(_keyCaregiverPhone) ?? '+1-555-0199',
      );
    } catch (_) {
      return const AppSettings();
    }
  }

  Future<void> saveSettings(AppSettings settings) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_keyBackendUrl, settings.backendUrl);
      if (settings.apiKey != null) {
        await prefs.setString(_keyApiKey, settings.apiKey!);
      } else {
        await prefs.remove(_keyApiKey);
      }
      await prefs.setBool(_keyMockMode, settings.useMockMode);
      await prefs.setString(_keyCaregiverName, settings.caregiverName);
      await prefs.setString(_keyCaregiverPhone, settings.caregiverPhone);
    } catch (_) {}
  }
}
