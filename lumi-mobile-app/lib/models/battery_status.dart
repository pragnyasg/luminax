class BatteryStatus {
  final double percentage;
  final double voltage;
  final double current;
  final bool isCharging;
  final bool isLow;

  const BatteryStatus({
    required this.percentage,
    required this.voltage,
    required this.current,
    required this.isCharging,
    required this.isLow,
  });

  factory BatteryStatus.fromJson(Map<String, dynamic> json) {
    final double pct = (json['percentage'] as num?)?.toDouble() ?? 100.0;
    return BatteryStatus(
      percentage: pct,
      voltage: (json['voltage'] as num?)?.toDouble() ?? 12.6,
      current: (json['current'] as num?)?.toDouble() ?? 0.5,
      isCharging: json['is_charging'] as bool? ?? false,
      isLow: json['is_low'] as bool? ?? (pct < 20.0),
    );
  }

  Map<String, dynamic> toJson() => {
    'percentage': percentage,
    'voltage': voltage,
    'current': current,
    'is_charging': isCharging,
    'is_low': isLow,
  };
}
