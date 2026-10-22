import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'theme/app_theme.dart';
import 'services/api_service.dart';
import 'services/websocket_service.dart';
import 'providers/settings_provider.dart';
import 'providers/robot_provider.dart';
import 'providers/navigation_provider.dart';
import 'providers/medicine_provider.dart';
import 'providers/emergency_provider.dart';
import 'providers/voice_provider.dart';
import 'screens/main_scaffold.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final settingsProvider = SettingsProvider();
  await settingsProvider.init();

  final initialUrl = settingsProvider.backendUrl;
  final apiService = ApiService(baseUrl: initialUrl);
  final wsService = WebSocketService();

  if (!settingsProvider.useMockMode) {
    wsService.connect(initialUrl);
  }

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider<SettingsProvider>.value(value: settingsProvider),
        ChangeNotifierProvider<RobotProvider>(
          create: (_) => RobotProvider(apiService: apiService, wsService: wsService),
        ),
        ChangeNotifierProvider<NavigationProvider>(
          create: (_) => NavigationProvider(apiService: apiService, wsService: wsService),
        ),
        ChangeNotifierProvider<MedicineProvider>(
          create: (_) => MedicineProvider(apiService: apiService),
        ),
        ChangeNotifierProvider<EmergencyProvider>(
          create: (_) => EmergencyProvider(apiService: apiService, wsService: wsService),
        ),
        ChangeNotifierProvider<VoiceProvider>(
          create: (_) => VoiceProvider(apiService: apiService),
        ),
      ],
      child: const LumiCaregiverApp(),
    ),
  );
}

class LumiCaregiverApp extends StatelessWidget {
  const LumiCaregiverApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LUMI Caregiver',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      home: const MainScaffold(),
    );
  }
}
