class Destination {
  final String id;
  final String name;
  final double x;
  final double y;
  final double theta;
  final String? description;

  const Destination({
    required this.id,
    required this.name,
    required this.x,
    required this.y,
    this.theta = 0.0,
    this.description,
  });

  factory Destination.fromJson(Map<String, dynamic> json) {
    return Destination(
      id: json['id'] as String,
      name: json['name'] as String,
      x: (json['x'] as num).toDouble(),
      y: (json['y'] as num).toDouble(),
      theta: (json['theta'] as num?)?.toDouble() ?? 0.0,
      description: json['description'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'x': x,
    'y': y,
    'theta': theta,
    'description': description,
  };
}

class NavigationGoal {
  final String goalId;
  final String destinationName;
  final double targetX;
  final double targetY;
  final String status;
  final double progressPercent;
  final double distanceRemainingM;
  final double estimatedSecondsRemaining;
  final String createdAt;

  const NavigationGoal({
    required this.goalId,
    required this.destinationName,
    required this.targetX,
    required this.targetY,
    required this.status,
    required this.progressPercent,
    required this.distanceRemainingM,
    required this.estimatedSecondsRemaining,
    required this.createdAt,
  });

  factory NavigationGoal.fromJson(Map<String, dynamic> json) {
    return NavigationGoal(
      goalId: json['goal_id'] as String? ?? 'none',
      destinationName: json['destination_name'] as String? ?? 'Target',
      targetX: (json['target_x'] as num?)?.toDouble() ?? 0.0,
      targetY: (json['target_y'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] as String? ?? 'IDLE',
      progressPercent: (json['progress_percent'] as num?)?.toDouble() ?? 0.0,
      distanceRemainingM: (json['distance_remaining_m'] as num?)?.toDouble() ?? 0.0,
      estimatedSecondsRemaining: (json['estimated_seconds_remaining'] as num?)?.toDouble() ?? 0.0,
      createdAt: json['created_at'] as String? ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() => {
    'goal_id': goalId,
    'destination_name': destinationName,
    'target_x': targetX,
    'target_y': targetY,
    'status': status,
    'progress_percent': progressPercent,
    'distance_remaining_m': distanceRemainingM,
    'estimated_seconds_remaining': estimatedSecondsRemaining,
    'created_at': createdAt,
  };
}
