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
      id: json['id'] as String? ?? 'act-${DateTime.now().millisecondsSinceEpoch}',
      timestamp: json['timestamp'] as String? ?? 'Just now',
      category: json['category'] as String? ?? 'general',
      severity: json['severity'] as String? ?? 'INFO',
      title: json['title'] as String? ?? 'Activity Event',
      description: json['description'] as String? ?? '',
      metadata: json['metadata'] as Map<String, dynamic>? ?? {},
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'timestamp': timestamp,
    'category': category,
    'severity': severity,
    'title': title,
    'description': description,
    'metadata': metadata,
  };
}

typedef ActivityLog = ActivityTimelineItem;
