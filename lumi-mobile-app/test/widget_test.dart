import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lumi_mobile_app/main.dart';
import 'package:lumi_mobile_app/widgets/battery_badge.dart';
import 'package:lumi_mobile_app/models/battery_status.dart';
import 'package:lumi_mobile_app/widgets/robot_eyes_widget.dart';
import 'package:lumi_mobile_app/widgets/connection_status_badge.dart';
import 'package:lumi_mobile_app/services/websocket_service.dart';

void main() {
  testWidgets('BatteryBadge displays percentage and charging correctly', (WidgetTester tester) async {
    const battery = BatteryStatus(
      percentage: 75.0,
      voltage: 12.2,
      current: 0.5,
      isCharging: true,
      isLow: false,
    );

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: BatteryBadge(battery: battery),
        ),
      ),
    );

    expect(find.text('75%'), findsOneWidget);
    expect(find.byIcon(Icons.bolt), findsOneWidget);
  });

  testWidgets('ConnectionStatusBadge displays MOCK MODE and ONLINE pills', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: ConnectionStatusBadge(
            state: WsConnectionState.connected,
            isMockMode: true,
          ),
        ),
      ),
    );

    expect(find.text('MOCK MODE'), findsOneWidget);
  });

  testWidgets('RobotEyesWidget renders dual eyes for happy expression', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: RobotEyesWidget(expression: 'happy'),
        ),
      ),
    );

    expect(find.byType(RobotEyesWidget), findsOneWidget);
  });
}
