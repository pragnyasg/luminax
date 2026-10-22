class MedicineSchedule {
  final String id;
  final String name;
  final String dosage;
  final String scheduledTime;
  final List<String> daysOfWeek;
  final String? instructions;
  final bool isActive;
  final String createdAt;

  const MedicineSchedule({
    required this.id,
    required this.name,
    required this.dosage,
    required this.scheduledTime,
    required this.daysOfWeek,
    this.instructions,
    this.isActive = true,
    required this.createdAt,
  });

  factory MedicineSchedule.fromJson(Map<String, dynamic> json) {
    return MedicineSchedule(
      id: json['id'] as String,
      name: json['name'] as String,
      dosage: json['dosage'] as String,
      scheduledTime: json['scheduled_time'] as String,
      daysOfWeek: List<String>.from(json['days_of_week'] as List? ?? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
      instructions: json['instructions'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] as String? ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'dosage': dosage,
    'scheduled_time': scheduledTime,
    'days_of_week': daysOfWeek,
    'instructions': instructions,
    'is_active': isActive,
    'created_at': createdAt,
  };
}

class MedicineLogEntry {
  final String id;
  final String medicineId;
  final String medicineName;
  final String dosage;
  final String scheduledTime;
  final String status; // pending, spoken, taken, skipped, missed
  final String? confirmedBy;
  final String? confirmedAt;
  final String? notes;

  const MedicineLogEntry({
    required this.id,
    required this.medicineId,
    required this.medicineName,
    required this.dosage,
    required this.scheduledTime,
    required this.status,
    this.confirmedBy,
    this.confirmedAt,
    this.notes,
  });

  factory MedicineLogEntry.fromJson(Map<String, dynamic> json) {
    return MedicineLogEntry(
      id: json['id'] as String,
      medicineId: json['medicine_id'] as String,
      medicineName: json['medicine_name'] as String,
      dosage: json['dosage'] as String,
      scheduledTime: json['scheduled_time'] as String,
      status: json['status'] as String? ?? 'pending',
      confirmedBy: json['confirmed_by'] as String?,
      confirmedAt: json['confirmed_at'] as String?,
      notes: json['notes'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'medicine_id': medicineId,
    'medicine_name': medicineName,
    'dosage': dosage,
    'scheduled_time': scheduledTime,
    'status': status,
    'confirmed_by': confirmedBy,
    'confirmed_at': confirmedAt,
    'notes': notes,
  };
}

class AdherenceSummary {
  final int totalDoses;
  final int takenCount;
  final int skippedCount;
  final int missedCount;
  final double adherenceRatePercent;

  const AdherenceSummary({
    required this.totalDoses,
    required this.takenCount,
    required this.skippedCount,
    required this.missedCount,
    required this.adherenceRatePercent,
  });

  factory AdherenceSummary.fromJson(Map<String, dynamic> json) {
    return AdherenceSummary(
      totalDoses: json['total_doses'] as int? ?? 0,
      takenCount: json['taken_count'] as int? ?? 0,
      skippedCount: json['skipped_count'] as int? ?? 0,
      missedCount: json['missed_count'] as int? ?? 0,
      adherenceRatePercent: (json['adherence_rate_percent'] as num?)?.toDouble() ?? 100.0,
    );
  }
}
