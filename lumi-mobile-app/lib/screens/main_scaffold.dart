import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/emergency_provider.dart';
import '../providers/settings_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/emergency_banner.dart';
import 'home_screen.dart';
import 'camera_screen.dart';
import 'map_screen.dart';
import 'medicines_screen.dart';
import 'more_screen.dart';

class MainScaffold extends StatefulWidget {
  const MainScaffold({Key? key}) : super(key: key);

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int _currentIndex = 0;

  void _onTabSelected(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final emergencyProv = context.watch<EmergencyProvider>();
    final settingsProv = context.watch<SettingsProvider>();

    final screens = [
      HomeScreen(onNavigateTab: _onTabSelected),
      const CameraScreen(),
      const MapScreen(),
      const MedicinesScreen(),
      const MoreScreen(),
    ];

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Global Persistent Emergency Banner across all tabs
            if (emergencyProv.hasActiveEmergency && emergencyProv.latestActiveEmergency != null)
              EmergencyBanner(
                event: emergencyProv.latestActiveEmergency!,
                onAcknowledge: () {
                  emergencyProv.acknowledgeEmergency(
                    emergencyProv.latestActiveEmergency!.eventId,
                    'Caregiver',
                  );
                },
                onCallResponder: () {
                  emergencyProv.callResponder(
                    emergencyProv.latestActiveEmergency!.eventId,
                    phone: settingsProv.settings.caregiverPhone,
                  );
                },
              ),

            // Tab View Body
            Expanded(
              child: IndexedStack(
                index: _currentIndex,
                children: screens,
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: _onTabSelected,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.videocam_outlined),
            selectedIcon: Icon(Icons.videocam_rounded),
            label: 'Camera',
          ),
          NavigationDestination(
            icon: Icon(Icons.map_outlined),
            selectedIcon: Icon(Icons.map_rounded),
            label: 'Map',
          ),
          NavigationDestination(
            icon: Icon(Icons.medication_outlined),
            selectedIcon: Icon(Icons.medication_rounded),
            label: 'Medicines',
          ),
          NavigationDestination(
            icon: Icon(Icons.grid_view_outlined),
            selectedIcon: Icon(Icons.grid_view_rounded),
            label: 'More',
          ),
        ],
      ),
    );
  }
}
