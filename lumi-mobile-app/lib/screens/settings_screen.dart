import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';
import '../providers/robot_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlCtrl;
  late TextEditingController _nameCtrl;
  late TextEditingController _phoneCtrl;

  @override
  void initState() {
    super.initState();
    final settings = context.read<SettingsProvider>().settings;
    _urlCtrl = TextEditingController(text: settings.backendUrl);
    _nameCtrl = TextEditingController(text: settings.caregiverName);
    _phoneCtrl = TextEditingController(text: settings.caregiverPhone);
  }

  @override
  void dispose() {
    _urlCtrl.dispose();
    _nameCtrl.dispose();
    _phoneCtrl.dispose();
    super.dispose();
  }

  void _saveSettings() {
    final settingsProv = context.read<SettingsProvider>();
    final robotProv = context.read<RobotProvider>();

    final updated = settingsProv.settings.copyWith(
      backendUrl: _urlCtrl.text.trim(),
      caregiverName: _nameCtrl.text.trim(),
      caregiverPhone: _phoneCtrl.text.trim(),
    );
    settingsProv.updateSettings(updated);
    robotProv.updateConfig(
      useMockMode: updated.useMockMode,
      backendUrl: updated.backendUrl,
    );

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Settings saved successfully.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final settingsProv = context.watch<SettingsProvider>();
    final robotProv = context.watch<RobotProvider>();
    final settings = settingsProv.settings;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings & Configuration'),
      ),
      body: ListView(
        padding: const EdgeInsets.only(bottom: 24),
        children: [
          // 1. Backend Server Connection Card
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Robot Backend Connection',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                const SizedBox(height: 6),
                Text(
                  'Enter the IP address of your Raspberry Pi 5 or local workstation running the FastAPI backend.',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _urlCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Backend URL (HTTP / IP:Port)',
                    hintText: 'http://192.168.1.100:8000',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: _saveSettings,
                      icon: const Icon(Icons.save_outlined, size: 16),
                      label: const Text('Save & Apply'),
                    ),
                    const SizedBox(width: 8),
                    OutlinedButton.icon(
                      onPressed: () async {
                        await robotProv.refreshStatus();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                robotProv.isConnected
                                    ? 'Connected to LUMI Backend successfully!'
                                    : 'Connection failed. Check network or enable Mock Mode.',
                              ),
                            ),
                          );
                        }
                      },
                      icon: const Icon(Icons.electrical_services_outlined, size: 16),
                      label: const Text('Test Ping'),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // 2. Mock Development Mode Toggle Card
          CustomCard(
            child: SwitchListTile(
              title: const Text('Mock Development Mode', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
              subtitle: const Text(
                'Simulate complete robot telemetry, Nav2 goals, fall alerts, and camera feeds without physical hardware.',
                style: TextStyle(fontSize: 12),
              ),
              value: settings.useMockMode,
              onChanged: (val) {
                settingsProv.setMockMode(val);
                robotProv.updateConfig(
                  useMockMode: val,
                  backendUrl: settings.backendUrl,
                );
              },
            ),
          ),

          // 3. Caregiver Profile Card
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Caregiver & Emergency Contacts',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _nameCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Primary Caregiver Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _phoneCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Emergency Contact Phone Number',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),

          // 4. System Diagnostics & Info
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'System Diagnostics & Versions',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                const SizedBox(height: 10),
                _buildInfoRow('LUMI Mobile App Version', '1.0.0+1'),
                _buildInfoRow('Backend API Version', '1.0.0 (FastAPI v1)'),
                _buildInfoRow('ROS 2 Distribution', 'Humble Hawksbill / Iron / Jazzy'),
                _buildInfoRow('Operating Target', 'Raspberry Pi 5 (Ubuntu 24.04/22.04)'),
                _buildInfoRow('Motor Bridge', 'ESP32 Serial 115200 Baud'),
                _buildInfoRow('Vision Stack', 'MediaPipe Pose + FaceNet + SQLite'),
                _buildInfoRow('Voice Pipeline', 'Faster-Whisper + Ollama + Piper'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade700, fontSize: 12)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
        ],
      ),
    );
  }
}
