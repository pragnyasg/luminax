import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/destination.dart';
import '../providers/navigation_provider.dart';
import '../providers/robot_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class MapScreen extends StatelessWidget {
  const MapScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final navProv = context.watch<NavigationProvider>();
    final robotProv = context.watch<RobotProvider>();

    final destinations = navProv.destinations;
    final currentGoal = navProv.currentGoal;
    final pose = robotProv.location;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Indoor Map & Navigation'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Map & Goals',
            onPressed: () => navProv.loadNavigationData(),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.only(bottom: 24),
        children: [
          // 1. Interactive 2D Map Canvas
          Container(
            height: 280,
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF231E2D),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: Colors.white12),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: CustomPaint(
                painter: _MapCanvasPainter(
                  robotX: pose.x,
                  robotY: pose.y,
                  robotTheta: pose.theta,
                  destinations: destinations,
                  activeGoal: currentGoal,
                ),
              ),
            ),
          ),

          // 2. Active Navigation Progress Card (if executing)
          if (currentGoal != null && currentGoal.status == 'EXECUTING')
            CustomCard(
              backgroundColor: LumiColors.primaryContainer.withOpacity(0.5),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.navigation_rounded, color: LumiColors.primary, size: 22),
                          const SizedBox(width: 8),
                          Text(
                            'Navigating to ${currentGoal.destinationName}',
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: LumiColors.primary,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          '${currentGoal.progressPercent.toInt()}%',
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  LinearProgressIndicator(
                    value: (currentGoal.progressPercent / 100.0).clamp(0.0, 1.0),
                    backgroundColor: Colors.white60,
                    valueColor: const AlwaysStoppedAnimation<Color>(LumiColors.primary),
                    minHeight: 6,
                    borderRadius: BorderRadius.circular(3),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Distance remaining: ${currentGoal.distanceRemainingM.toStringAsFixed(1)} m',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                      ),
                      Text(
                        'Est. time: ${currentGoal.estimatedSecondsRemaining.toInt()}s',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: () => navProv.cancelGoal(),
                    icon: const Icon(Icons.cancel_outlined, size: 18),
                    label: const Text('Cancel Navigation'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: LumiColors.emergency,
                      foregroundColor: Colors.white,
                      minimumSize: const Size.fromHeight(40),
                    ),
                  ),
                ],
              ),
            ),

          // 3. Saved Destinations Dispatch Grid
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: const Text(
              'Saved Destinations',
              style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
            ),
          ),
          ...destinations.map((dest) {
            final isTarget = currentGoal != null && currentGoal.destinationName == dest.name && currentGoal.status == 'EXECUTING';

            return CustomCard(
              child: ListTile(
                leading: Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: isTarget ? LumiColors.primary : LumiColors.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getDestinationIcon(dest.name),
                    color: isTarget ? Colors.white : LumiColors.primary,
                    size: 22,
                  ),
                ),
                title: Text(
                  dest.name,
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                subtitle: Text(
                  dest.description ?? 'Coords: (${dest.x.toStringAsFixed(1)}, ${dest.y.toStringAsFixed(1)})',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
                trailing: ElevatedButton(
                  onPressed: () => navProv.dispatchGoalToDestination(dest),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: isTarget ? Colors.grey : LumiColors.primary,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  ),
                  child: Text(
                    isTarget ? 'Active' : 'Go Here',
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  IconData _getDestinationIcon(String name) {
    final lower = name.toLowerCase();
    if (lower.contains('bed')) return Icons.bed_outlined;
    if (lower.contains('kitchen')) return Icons.kitchen_outlined;
    if (lower.contains('medicine')) return Icons.medical_services_outlined;
    if (lower.contains('dock') || lower.contains('charge')) return Icons.bolt_outlined;
    return Icons.chair_outlined;
  }
}

class _MapCanvasPainter extends CustomPainter {
  final double robotX;
  final double robotY;
  final double robotTheta;
  final List<Destination> destinations;
  final NavigationGoal? activeGoal;

  _MapCanvasPainter({
    required this.robotX,
    required this.robotY,
    required this.robotTheta,
    required this.destinations,
    this.activeGoal,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    const scale = 25.0; // pixels per meter

    // 1. Draw subtle coordinate grid lines
    final gridPaint = Paint()
      ..color = Colors.white.withOpacity(0.06)
      ..strokeWidth = 1.0;

    for (double x = 0; x < size.width; x += 30) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
    }
    for (double y = 0; y < size.height; y += 30) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    // 2. Draw destination markers
    final destPaint = Paint()
      ..color = const Color(0xFF6750A4)
      ..style = PaintingStyle.fill;

    for (final d in destinations) {
      final destOffset = Offset(center.dx + (d.x * scale), center.dy - (d.y * scale));
      canvas.drawCircle(destOffset, 8, destPaint);

      // Text label
      final textSpan = TextSpan(
        text: d.name,
        style: const TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.w600),
      );
      final textPainter = TextPainter(text: textSpan, textDirection: TextDirection.ltr);
      textPainter.layout();
      textPainter.paint(canvas, Offset(destOffset.dx - (textPainter.width / 2), destOffset.dy + 10));
    }

    // 3. Draw robot marker with heading
    final robotOffset = Offset(center.dx + (robotX * scale), center.dy - (robotY * scale));
    final robotPaint = Paint()
      ..color = const Color(0xFF00E676)
      ..style = PaintingStyle.fill;

    // Robot body circle
    canvas.drawCircle(robotOffset, 12, robotPaint);

    // Direction heading line
    final headingPaint = Paint()
      ..color = Colors.white
      ..strokeWidth = 3.0;

    final headingEnd = Offset(
      robotOffset.dx + (18 * scale / 25 * 1.0 * (robotTheta == 0 ? 1 : 0.8)),
      robotOffset.dy - (18 * scale / 25 * 0.4),
    );
    canvas.drawLine(robotOffset, headingEnd, headingPaint);
  }

  @override
  bool shouldRepaint(covariant _MapCanvasPainter oldDelegate) => true;
}
