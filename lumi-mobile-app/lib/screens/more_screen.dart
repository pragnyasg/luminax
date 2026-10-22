import 'package:flutter/material.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';
import 'voice_screen.dart';
import 'controls_screen.dart';
import 'people_screen.dart';
import 'history_screen.dart';
import 'emergency_screen.dart';
import 'settings_screen.dart';

class MoreScreen extends StatelessWidget {
  const MoreScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('More Capabilities & Tools'),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: 8),
        children: [
          _buildItem(
            context,
            title: 'Voice & Speech Assistant',
            subtitle: 'Conversation history, TTS, and text commands',
            icon: Icons.record_voice_over_outlined,
            color: LumiColors.info,
            destination: const VoiceScreen(),
          ),
          _buildItem(
            context,
            title: 'Manual Teleoperation Pad',
            subtitle: 'Directional controls, speed limits, and emergency stop',
            icon: Icons.gamepad_outlined,
            color: LumiColors.warning,
            destination: const ControlsScreen(),
          ),
          _buildItem(
            context,
            title: 'People & Activity Tracking',
            subtitle: 'Identities, posture detection, and presence monitor',
            icon: Icons.people_outline,
            color: LumiColors.primary,
            destination: const PeopleScreen(),
          ),
          _buildItem(
            context,
            title: 'Activity & Event History',
            subtitle: 'Searchable timeline of reminders, alerts, and navigation',
            icon: Icons.history_rounded,
            color: Colors.blueGrey,
            destination: const HistoryScreen(),
          ),
          _buildItem(
            context,
            title: 'Emergency & Fall Events',
            subtitle: 'Critical alarms, acknowledgment logs, and phone dispatch',
            icon: Icons.warning_amber_rounded,
            color: LumiColors.emergency,
            destination: const EmergencyScreen(),
          ),
          _buildItem(
            context,
            title: 'Settings & Diagnostics',
            subtitle: 'Backend URL, mock mode toggle, contacts, and subsystem health',
            icon: Icons.settings_outlined,
            color: LumiColors.secondary,
            destination: const SettingsScreen(),
          ),
        ],
      ),
    );
  }

  Widget _buildItem(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required Widget destination,
  }) {
    return CustomCard(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => destination),
        );
      },
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ],
            ),
          ),
          const Icon(Icons.chevron_right, color: Colors.grey),
        ],
      ),
    );
  }
}
