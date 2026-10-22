class PersonTrack {
  final int trackId;
  final String? personName;
  final double confidence;
  final String posture;
  final String presenceState;
  final String lastSeenTimestamp;
  final List<int>? bbox;

  const PersonTrack({
    required this.trackId,
    this.personName,
    required this.confidence,
    required this.posture,
    required this.presenceState,
    required this.lastSeenTimestamp,
    this.bbox,
  });

  factory PersonTrack.fromJson(Map<String, dynamic> json) {
    return PersonTrack(
      trackId: json['track_id'] as int? ?? 1,
      personName: json['person_name'] as String? ?? 'Primary Patient',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.9,
      posture: json['posture'] as String? ?? 'sitting',
      presenceState: json['presence_state'] as String? ?? 'PRESENT',
      lastSeenTimestamp: json['last_seen_timestamp'] as String? ?? DateTime.now().toIso8601String(),
      bbox: json['bbox'] != null ? List<int>.from(json['bbox'] as List) : null,
    );
  }
}

class ActivityTimelineItem {
  final String id;
  final String timestamp;
  final String category; // medicine, emergency, navigation, voice, system, presence
  final String severity; // INFO, WARNING, ALERT, CRITICAL
  final String title;
  final String description;
  final Map<String, dynamic> metadata;

  const ActivityTimelineItem({
    required this.id,
    required this.timestamp,
    required this.category,
    required this.severity,
    required this.title,
    required this.description,
    this.metadata = const {},
  });

  factory ActivityTimelineItem.fromJson(Map<String, dynamic> json) {
    return ActivityTimelineItem(
      id: json['id'] as String? ?? 'act-0',
      timestamp: json['timestamp'] as String? ?? DateTime.now().toIso8601String(),
      category: json['category'] as String? ?? 'system',
      severity: json['severity'] as String? ?? 'INFO',
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      metadata: json['metadata'] as Map<String, dynamic>? ?? {},
    );
  }
}
