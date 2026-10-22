import 'robot_status.dart';

class EmergencyEvent {
  final String eventId;
  final String eventType;
  final String severity;
  final String timestamp;
  final double confidence;
  final String? personName;
  final String posture;
  final Pose2D? location;
  final String? snapshotUrl;
  final bool acknowledged;
  final String? acknowledgedAt;
  final String? acknowledgedBy;
  final String? resolutionNotes;

  const EmergencyEvent({
    required this.eventId,
    required this.eventType,
    required this.severity,
    required this.timestamp,
    required this.confidence,
    this.personName,
    required this.posture,
    this.location,
    this.snapshotUrl,
    required this.acknowledged,
    this.acknowledgedAt,
    this.acknowledgedBy,
    this.resolutionNotes,
  });

  factory EmergencyEvent.fromJson(Map<String, dynamic> json) {
    return EmergencyEvent(
      eventId: json['event_id'] as String,
      eventType: json['event_type'] as String? ?? 'fall_confirmed',
      severity: json['severity'] as String? ?? 'CRITICAL',
      timestamp: json['timestamp'] as String? ?? DateTime.now().toIso8601String(),
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.95,
      personName: json['person_name'] as String? ?? 'Primary Patient',
      posture: json['posture'] as String? ?? 'lying_down',
      location: Pose2D.fromJson(json['location'] as Map<String, dynamic>?),
      snapshotUrl: json['snapshot_url'] as String?,
      acknowledged: json['acknowledged'] as bool? ?? false,
      acknowledgedAt: json['acknowledged_at'] as String?,
      acknowledgedBy: json['acknowledged_by'] as String?,
      resolutionNotes: json['resolution_notes'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'event_id': eventId,
    'event_type': eventType,
    'severity': severity,
    'timestamp': timestamp,
    'confidence': confidence,
    'person_name': personName,
    'posture': posture,
    'location': location?.toJson(),
    'snapshot_url': snapshotUrl,
    'acknowledged': acknowledged,
    'acknowledged_at': acknowledgedAt,
    'acknowledged_by': acknowledgedBy,
    'resolution_notes': resolutionNotes,
  };
}
