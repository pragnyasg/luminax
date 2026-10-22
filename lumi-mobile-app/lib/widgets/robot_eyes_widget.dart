import 'dart:async';
import 'package:flutter/material.dart';
import '../theme/lumi_colors.dart';

class RobotEyesWidget extends StatefulWidget {
  final String expression; // happy, listening, thinking, alert, emergency, sleeping
  final double width;
  final double height;

  const RobotEyesWidget({
    Key? key,
    this.expression = 'happy',
    this.width = 160,
    this.height = 70,
  }) : super(key: key);

  @override
  State<RobotEyesWidget> createState() => _RobotEyesWidgetState();
}

class _RobotEyesWidgetState extends State<RobotEyesWidget> with SingleTickerProviderStateMixin {
  late AnimationController _blinkController;
  Timer? _periodicBlinkTimer;

  @override
  void initState() {
    super.initState();
    _blinkController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    );

    _periodicBlinkTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      if (mounted && widget.expression != 'sleeping' && widget.expression != 'emergency') {
        _blinkController.forward().then((_) {
          if (mounted) _blinkController.reverse();
        });
      }
    });
  }

  @override
  void dispose() {
    _blinkController.dispose();
    _periodicBlinkTimer?.cancel();
    super.dispose();
  }

  Color _getEyeColor() {
    switch (widget.expression.toLowerCase()) {
      case 'emergency':
        return LumiColors.robotEyeAlert;
      case 'alert':
        return LumiColors.warning;
      case 'listening':
        return LumiColors.info;
      case 'thinking':
        return Colors.amber.shade700;
      case 'sleeping':
        return Colors.white54;
      case 'happy':
      default:
        return const Color(0xFF9D84FF);
    }
  }

  @override
  Widget build(BuildContext context) {
    final eyeColor = _getEyeColor();
    final isSleeping = widget.expression.toLowerCase() == 'sleeping';

    return Container(
      width: widget.width,
      height: widget.height,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: LumiColors.robotEyeBackground,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: widget.expression == 'emergency' ? LumiColors.emergency : Colors.white12,
          width: widget.expression == 'emergency' ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: eyeColor.withOpacity(0.25),
            blurRadius: 16,
            spreadRadius: 2,
          ),
        ],
      ),
      child: AnimatedBuilder(
        animation: _blinkController,
        builder: (context, _) {
          final double blinkScale = 1.0 - (_blinkController.value * 0.85);

          return Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildSingleEye(eyeColor, blinkScale, isSleeping, isLeft: true),
              _buildSingleEye(eyeColor, blinkScale, isSleeping, isLeft: false),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSingleEye(Color color, double scaleY, bool isSleeping, {required bool isLeft}) {
    if (isSleeping) {
      return Container(
        width: 32,
        height: 6,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(3),
        ),
      );
    }

    final isHappy = widget.expression.toLowerCase() == 'happy';

    return Transform.scale(
      scaleY: scaleY,
      child: Container(
        width: 34,
        height: 38,
        decoration: BoxDecoration(
          color: color,
          borderRadius: isHappy
              ? const BorderRadius.vertical(top: Radius.circular(18), bottom: Radius.circular(8))
              : BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.6),
              blurRadius: 8,
              spreadRadius: 1,
            ),
          ],
        ),
        child: Center(
          child: Container(
            width: 10,
            height: 10,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
          ),
        ),
      ),
    );
  }
}
