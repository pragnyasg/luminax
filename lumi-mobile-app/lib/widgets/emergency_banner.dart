import 'package:flutter/material.dart';
import '../models/emergency_event.dart';
import '../theme/lumi_colors.dart';

class EmergencyBanner extends StatelessWidget {
  final EmergencyEvent event;
  final VoidCallback onAcknowledge;
  final VoidCallback onCallResponder;

  const EmergencyBanner({
    Key? key,
    required this.event,
    required this.onAcknowledge,
    required this.onCallResponder,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LumiColors.emergency,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: LumiColors.emergency.withOpacity(0.35),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.warning_amber_rounded, color: Colors.white, size: 28),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'EMERGENCY: ${event.eventType.replaceAll('_', ' ').toUpperCase()}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                        fontSize: 15,
                        letterSpacing: 0.3,
                      ),
                    ),
                    Text(
                      'Detected with ${(event.confidence * 100).toInt()}% confidence. Posture: ${event.posture.replaceAll('_', ' ').toUpperCase()}',
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: onAcknowledge,
                  icon: const Icon(Icons.check_circle_outline, size: 18),
                  label: const Text('Acknowledge'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: LumiColors.emergency,
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onCallResponder,
                  icon: const Icon(Icons.phone, size: 18, color: Colors.white),
                  label: const Text('Call Contact', style: TextStyle(color: Colors.white)),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.white, width: 1.5),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
