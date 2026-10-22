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

  Map<String, dynamic> toJson() => {
    'track_id': trackId,
    'person_name': personName,
    'confidence': confidence,
    'posture': posture,
    'presence_state': presenceState,
    'last_seen_timestamp': lastSeenTimestamp,
    'bbox': bbox,
  };
}
