import 'package:flutter/material.dart';
import '../models/battery_status.dart';
import '../theme/lumi_colors.dart';

class BatteryBadge extends StatelessWidget {
  final BatteryStatus battery;

  const BatteryBadge({Key? key, required this.battery}) : super(key: key);

  Color _getBatteryColor() {
    if (battery.isCharging) return LumiColors.info;
    if (battery.percentage <= 20) return LumiColors.emergency;
    if (battery.percentage <= 45) return LumiColors.warning;
    return LumiColors.success;
  }

  IconData _getBatteryIcon() {
    if (battery.isCharging) return Icons.bolt;
    if (battery.percentage <= 15) return Icons.battery_alert;
    if (battery.percentage <= 35) return Icons.battery_2_bar;
    if (battery.percentage <= 65) return Icons.battery_4_bar;
    if (battery.percentage <= 85) return Icons.battery_5_bar;
    return Icons.battery_full;
  }

  @override
  Widget build(BuildContext context) {
    final color = _getBatteryColor();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getBatteryIcon(), size: 18, color: color),
          const SizedBox(width: 4),
          Text(
            '${battery.percentage.toInt()}%',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w700,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }
}
