import 'battery_status.dart';

class Pose2D {
  final double x;
  final double y;
  final double theta;
  final String frameId;

  const Pose2D({
    this.x = 0.0,
    this.y = 0.0,
    this.theta = 0.0,
    this.frameId = 'map',
  });

  factory Pose2D.fromJson(Map<String, dynamic>? json) {
    if (json == null) return const Pose2D();
    return Pose2D(
      x: (json['x'] as num?)?.toDouble() ?? 0.0,
      y: (json['y'] as num?)?.toDouble() ?? 0.0,
      theta: (json['theta'] as num?)?.toDouble() ?? 0.0,
      frameId: json['frame_id'] as String? ?? 'map',
    );
  }

  Map<String, dynamic> toJson() => {
    'x': x,
    'y': y,
    'theta': theta,
    'frame_id': frameId,
  };
}

class RobotStatus {
  final String robotId;
  final String name;
  final bool isConnected;
  final bool devMode;
  final String operatingMode;
  final String currentActivity;
  final String expression;
  final BatteryStatus battery;
  final Pose2D location;
  final int unacknowledgedEmergencies;
  final String? nextMedicineReminder;
  final String lastHeartbeat;

  const RobotStatus({
    required this.robotId,
    required this.name,
    required this.isConnected,
    required this.devMode,
    required this.operatingMode,
    required this.currentActivity,
    required this.expression,
    required this.battery,
    required this.location,
    required this.unacknowledgedEmergencies,
    this.nextMedicineReminder,
    required this.lastHeartbeat,
  });

  factory RobotStatus.fromJson(Map<String, dynamic> json) {
    return RobotStatus(
      robotId: json['robot_id'] as String? ?? 'lumi-01',
      name: json['name'] as String? ?? 'LUMI Healthcare Companion',
      isConnected: json['is_connected'] as bool? ?? false,
      devMode: json['dev_mode'] as bool? ?? false,
      operatingMode: json['operating_mode'] as String? ?? 'AUTONOMOUS',
      currentActivity: json['current_activity'] as String? ?? 'idle',
      expression: json['expression'] as String? ?? 'happy',
      battery: BatteryStatus.fromJson(json['battery'] as Map<String, dynamic>? ?? {}),
      location: Pose2D.fromJson(json['location'] as Map<String, dynamic>?),
      unacknowledgedEmergencies: json['unacknowledged_emergencies'] as int? ?? 0,
      nextMedicineReminder: json['next_medicine_reminder'] as String?,
      lastHeartbeat: json['last_heartbeat'] as String? ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() => {
    'robot_id': robotId,
    'name': name,
    'is_connected': isConnected,
    'dev_mode': devMode,
    'operating_mode': operatingMode,
    'current_activity': currentActivity,
    'expression': expression,
    'battery': battery.toJson(),
    'location': location.toJson(),
    'unacknowledged_emergencies': unacknowledgedEmergencies,
    'next_medicine_reminder': nextMedicineReminder,
    'last_heartbeat': lastHeartbeat,
  };
}
