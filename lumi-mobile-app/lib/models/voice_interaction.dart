class VoiceInteraction {
  final String id;
  final String timestamp;
  final String recognizedSpeech;
  final String responseText;
  final String speaker;
  final String source;

  const VoiceInteraction({
    required this.id,
    required this.timestamp,
    required this.recognizedSpeech,
    required this.responseText,
    this.speaker = 'LUMI',
    this.source = 'voice_node',
  });

  factory VoiceInteraction.fromJson(Map<String, dynamic> json) {
    return VoiceInteraction(
      id: json['id'] as String? ?? 'vox-0',
      timestamp: json['timestamp'] as String? ?? DateTime.now().toIso8601String(),
      recognizedSpeech: json['recognized_speech'] as String? ?? '',
      responseText: json['response_text'] as String? ?? '',
      speaker: json['speaker'] as String? ?? 'LUMI',
      source: json['source'] as String? ?? 'voice_node',
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'timestamp': timestamp,
    'recognized_speech': recognizedSpeech,
    'response_text': responseText,
    'speaker': speaker,
    'source': source,
  };
}

class AudioDevice {
  final int id;
  final String name;
  final String deviceType;
  final bool isDefault;

  const AudioDevice({
    required this.id,
    required this.name,
    required this.deviceType,
    required this.isDefault,
  });

  factory AudioDevice.fromJson(Map<String, dynamic> json) {
    return AudioDevice(
      id: json['id'] as int? ?? 0,
      name: json['name'] as String? ?? 'Default Device',
      deviceType: json['device_type'] as String? ?? 'output',
      isDefault: json['is_default'] as bool? ?? false,
    );
  }
}
