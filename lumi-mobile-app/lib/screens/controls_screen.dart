import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/robot_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';
import '../widgets/direction_pad.dart';

class ControlsScreen extends StatefulWidget {
  const ControlsScreen({Key? key}) : super(key: key);

  @override
  State<ControlsScreen> createState() => _ControlsScreenState();
}

class _ControlsScreenState extends State<ControlsScreen> {
  double _speedScale = 0.8; // 80% of max speed
  bool _safetyOverride = false;

  @override
  Widget build(BuildContext context) {
    final robotProv = context.watch<RobotProvider>();
    final status = robotProv.status;
    final isHalted = status.operatingMode == 'EMERGENCY_HALT';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Manual Robot Teleoperation'),
      ),
      body: ListView(
        padding: const EdgeInsets.only(bottom: 24),
        children: [
          // Safety warning banner if halted
          if (isHalted)
            CustomCard(
              backgroundColor: LumiColors.emergencyContainer,
              child: Row(
                children: [
                  const Icon(Icons.block, color: LumiColors.emergency, size: 28),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Motion blocked: Robot is in EMERGENCY_HALT mode. Clear emergency alert or enable safety override.',
                      style: TextStyle(color: LumiColors.emergency, fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),

          // 1. Teleoperation Direction Pad
          CustomCard(
            padding: const EdgeInsets.symmetric(vertical: 24),
            child: Column(
              children: [
                DirectionPad(
                  isEnabled: !isHalted || _safetyOverride,
                  onDirectionDown: (linear, angular) {
                    final scaledLinear = linear * _speedScale;
                    final scaledAngular = angular * _speedScale;
                    robotProv.sendManualControl(
                      scaledLinear,
                      scaledAngular,
                      safetyOverride: _safetyOverride,
                    );
                  },
                  onDirectionUp: () {
                    // Dead-man stop on release
                    robotProv.sendManualControl(0.0, 0.0);
                  },
                  onEmergencyStop: () {
                    robotProv.sendStop();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Emergency Stop Command Dispatched.')),
                    );
                  },
                ),
                const SizedBox(height: 16),
                Text(
                  'Dead-man safety: Motion halts automatically upon finger release.',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
                ),
              ],
            ),
          ),

          // 2. Speed Limits and Conservative Settings
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Speed Limits & Safety Settings',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Max Linear Speed: ${(0.35 * _speedScale).toStringAsFixed(2)} m/s'),
                    Text('Max Turn Rate: ${(0.80 * _speedScale).toStringAsFixed(2)} rad/s'),
                  ],
                ),
                Slider(
                  value: _speedScale,
                  min: 0.2,
                  max: 1.0,
                  divisions: 8,
                  label: '${(_speedScale * 100).toInt()}%',
                  onChanged: (val) {
                    setState(() {
                      _speedScale = val;
                    });
                  },
                ),
                SwitchListTile(
                  title: const Text('Safety Interlock Override', style: TextStyle(fontSize: 14)),
                  subtitle: const Text('Permits manual teleop even when alert is active', style: TextStyle(fontSize: 12)),
                  value: _safetyOverride,
                  onChanged: (val) {
                    setState(() {
                      _safetyOverride = val;
                    });
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
