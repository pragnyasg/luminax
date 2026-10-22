import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/robot_provider.dart';
import '../providers/emergency_provider.dart';
import '../providers/medicine_provider.dart';
import '../providers/settings_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/robot_eyes_widget.dart';
import '../widgets/battery_badge.dart';
import '../widgets/connection_status_badge.dart';
import '../widgets/custom_card.dart';

class HomeScreen extends StatelessWidget {
  final Function(int tabIndex) onNavigateTab;

  const HomeScreen({Key? key, required this.onNavigateTab}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final robotProv = context.watch<RobotProvider>();
    final emergencyProv = context.watch<EmergencyProvider>();
    final medicineProv = context.watch<MedicineProvider>();
    final settingsProv = context.watch<SettingsProvider>();

    final status = robotProv.status;
    final isMock = settingsProv.useMockMode;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'LUMI Companion',
              style: TextStyle(fontWeight: FontWeight.w700, fontSize: 19),
            ),
            Text(
              status.name,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ConnectionStatusBadge(
              state: robotProv.connectionState,
              isMockMode: isMock,
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: BatteryBadge(battery: status.battery),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await robotProv.refreshStatus();
          await emergencyProv.loadEmergencies();
          await medicineProv.loadMedicines();
        },
        child: ListView(
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            // 1. Robot Expression & Status Banner Card
            CustomCard(
              backgroundColor: LumiColors.primaryContainer.withOpacity(0.4),
              child: Column(
                children: [
                  Row(
                    children: [
                      RobotEyesWidget(expression: status.expression),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: LumiColors.primary,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                status.operatingMode,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Expression: ${status.expression.toUpperCase()}',
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 14,
                                color: LumiColors.onPrimaryContainer,
                              ),
                            ),
                            Text(
                              'Activity: ${status.currentActivity.replaceAll('_', ' ').toUpperCase()}',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade700,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Divider(height: 1),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Location: (${status.location.x.toStringAsFixed(1)}, ${status.location.y.toStringAsFixed(1)}) m',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade700, fontWeight: FontWeight.w500),
                      ),
                      Text(
                        'Updated: Just now',
                        style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // 2. Quick Action Grid
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: const Text(
                'Quick Controls',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, letterSpacing: -0.2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              child: Row(
                children: [
                  _buildQuickAction(
                    icon: Icons.videocam_outlined,
                    label: 'Live Camera',
                    color: LumiColors.info,
                    onTap: () => onNavigateTab(1), // Camera tab
                  ),
                  const SizedBox(width: 10),
                  _buildQuickAction(
                    icon: Icons.map_outlined,
                    label: 'Indoor Map',
                    color: LumiColors.primary,
                    onTap: () => onNavigateTab(2), // Map tab
                  ),
                  const SizedBox(width: 10),
                  _buildQuickAction(
                    icon: Icons.medication_outlined,
                    label: 'Medicines',
                    color: LumiColors.success,
                    onTap: () => onNavigateTab(3), // Medicines tab
                  ),
                  const SizedBox(width: 10),
                  _buildQuickAction(
                    icon: Icons.gamepad_outlined,
                    label: 'Teleop Pad',
                    color: LumiColors.warning,
                    onTap: () => onNavigateTab(4), // More tab (controls)
                  ),
                ],
              ),
            ),

            // 3. Next Scheduled Medicine Card
            CustomCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.access_time_rounded, color: LumiColors.primary, size: 20),
                          SizedBox(width: 8),
                          Text(
                            'Next Medicine Schedule',
                            style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                          ),
                        ],
                      ),
                      TextButton(
                        onPressed: () => onNavigateTab(3),
                        child: const Text('View All', style: TextStyle(fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: LumiColors.surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.black.withOpacity(0.04)),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: LumiColors.successContainer,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.medication, color: LumiColors.success, size: 22),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                status.nextMedicineReminder ?? 'Metformin (500mg)',
                                style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Scheduled for today | Active dose reminder',
                                style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        ElevatedButton(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Medicine reminder confirmed by caregiver.')),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: LumiColors.success,
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          ),
                          child: const Text('Confirm', style: TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // 4. Fall Detection & Safety Status Card
            CustomCard(
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: emergencyProv.hasActiveEmergency ? LumiColors.emergencyContainer : LumiColors.successContainer,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      emergencyProv.hasActiveEmergency ? Icons.warning_rounded : Icons.shield_outlined,
                      color: emergencyProv.hasActiveEmergency ? LumiColors.emergency : LumiColors.success,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          emergencyProv.hasActiveEmergency ? 'ACTIVE FALL ALERT' : 'Patient Safety Nominal',
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 14,
                            color: emergencyProv.hasActiveEmergency ? LumiColors.emergency : Colors.black87,
                          ),
                        ),
                        Text(
                          emergencyProv.hasActiveEmergency
                              ? 'Unacknowledged incident requires attention'
                              : 'Computer vision fall detector active with zero alerts',
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  if (!emergencyProv.hasActiveEmergency)
                    TextButton(
                      onPressed: () async {
                        await emergencyProv.simulateFall();
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Simulated fall event generated for testing.')),
                        );
                      },
                      child: const Text('Test Fall', style: TextStyle(fontSize: 11)),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickAction({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: color.withOpacity(0.08),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withOpacity(0.2)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: color, size: 26),
              const SizedBox(height: 6),
              Text(
                label,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w700,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
