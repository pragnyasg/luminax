import 'package:flutter/material.dart';
import '../services/websocket_service.dart';
import '../theme/lumi_colors.dart';

class ConnectionStatusBadge extends StatelessWidget {
  final WsConnectionState state;
  final bool isMockMode;

  const ConnectionStatusBadge({
    Key? key,
    required this.state,
    this.isMockMode = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (isMockMode) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: LumiColors.primaryContainer,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.science_outlined, size: 14, color: LumiColors.onPrimaryContainer),
            SizedBox(width: 4),
            Text(
              'MOCK MODE',
              style: TextStyle(
                color: LumiColors.onPrimaryContainer,
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      );
    }

    Color color;
    String label;
    IconData icon;

    switch (state) {
      case WsConnectionState.connected:
        color = LumiColors.success;
        label = 'ONLINE';
        icon = Icons.wifi;
        break;
      case WsConnectionState.connecting:
        color = LumiColors.warning;
        label = 'CONNECTING';
        icon = Icons.wifi_find;
        break;
      case WsConnectionState.disconnected:
      default:
        color = Colors.grey.shade600;
        label = 'OFFLINE';
        icon = Icons.wifi_off;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}
