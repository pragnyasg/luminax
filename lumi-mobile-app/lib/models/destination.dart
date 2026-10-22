export 'navigation_goal.dart';

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
