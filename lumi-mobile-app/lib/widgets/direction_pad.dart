import 'package:flutter/material.dart';
import '../theme/lumi_colors.dart';

class DirectionPad extends StatelessWidget {
  final Function(double linear, double angular) onDirectionDown;
  final VoidCallback onDirectionUp;
  final VoidCallback onEmergencyStop;
  final bool isEnabled;

  const DirectionPad({
    Key? key,
    required this.onDirectionDown,
    required this.onDirectionUp,
    required this.onEmergencyStop,
    this.isEnabled = true,
  }) : super(key: key);

  Widget _buildButton({
    required IconData icon,
    required double linear,
    required double angular,
    required String label,
  }) {
    return GestureDetector(
      onTapDown: isEnabled ? (_) => onDirectionDown(linear, angular) : null,
      onTapUp: isEnabled ? (_) => onDirectionUp() : null,
      onTapCancel: isEnabled ? onDirectionUp : null,
      child: Container(
        width: 70,
        height: 70,
        decoration: BoxDecoration(
          color: isEnabled ? LumiColors.primaryContainer : Colors.grey.shade300,
          shape: BoxShape.circle,
          boxShadow: [
            if (isEnabled)
              BoxShadow(
                color: LumiColors.primary.withOpacity(0.2),
                blurRadius: 8,
                offset: const Offset(0, 3),
              ),
          ],
        ),
        child: Icon(
          icon,
          size: 34,
          color: isEnabled ? LumiColors.onPrimaryContainer : Colors.grey.shade600,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Forward
        _buildButton(
          icon: Icons.keyboard_arrow_up_rounded,
          linear: 0.25,
          angular: 0.0,
          label: 'Forward',
        ),
        const SizedBox(height: 12),
        // Middle row: Left, STOP, Right
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildButton(
              icon: Icons.keyboard_arrow_left_rounded,
              linear: 0.0,
              angular: 0.6,
              label: 'Left',
            ),
            const SizedBox(width: 16),
            // Prominent STOP button
            GestureDetector(
              onTap: onEmergencyStop,
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: LumiColors.emergency,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: LumiColors.emergency.withOpacity(0.4),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: const Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.stop_rounded, size: 36, color: Colors.white),
                    Text(
                      'STOP',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 16),
            _buildButton(
              icon: Icons.keyboard_arrow_right_rounded,
              linear: 0.0,
              angular: -0.6,
              label: 'Right',
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Reverse
        _buildButton(
          icon: Icons.keyboard_arrow_down_rounded,
          linear: -0.2,
          angular: 0.0,
          label: 'Reverse',
        ),
      ],
    );
  }
}
