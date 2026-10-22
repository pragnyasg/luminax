class AppSettings {
  final String backendUrl;
  final String? apiKey;
  final bool useMockMode;
  final String caregiverName;
  final String caregiverPhone;
  final String emergencyPhone;
  final bool notificationsEnabled;
  final bool privacyShieldActive;

  const AppSettings({
    this.backendUrl = 'http://192.168.1.100:8000',
    this.apiKey,
    this.useMockMode = false,
    this.caregiverName = 'Primary Caregiver',
    this.caregiverPhone = '+1-555-0199',
    this.emergencyPhone = '+1-555-9110',
    this.notificationsEnabled = true,
    this.privacyShieldActive = false,
  });

  AppSettings copyWith({
    String? backendUrl,
    String? apiKey,
    bool? useMockMode,
    String? caregiverName,
    String? caregiverPhone,
    String? emergencyPhone,
    bool? notificationsEnabled,
    bool? privacyShieldActive,
  }) {
    return AppSettings(
      backendUrl: backendUrl ?? this.backendUrl,
      apiKey: apiKey ?? this.apiKey,
      useMockMode: useMockMode ?? this.useMockMode,
      caregiverName: caregiverName ?? this.caregiverName,
      caregiverPhone: caregiverPhone ?? this.caregiverPhone,
      emergencyPhone: emergencyPhone ?? this.emergencyPhone,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      privacyShieldActive: privacyShieldActive ?? this.privacyShieldActive,
    );
  }
}
