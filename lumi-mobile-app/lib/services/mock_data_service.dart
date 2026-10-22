import 'dart:async';
import '../models/robot_status.dart';
import '../models/battery_status.dart';
import '../models/destination.dart';
import '../models/navigation_goal.dart';
import '../models/medicine.dart';
import '../models/emergency_event.dart';
import '../models/voice_interaction.dart';
import '../models/person_track.dart';
import '../models/activity_log.dart';

class MockDataService {
  static RobotStatus getMockRobotStatus() {
    return const RobotStatus(
      robotId: 'lumi-mock-01',
      name: 'LUMI Healthcare Companion [OFFLINE MOCK]',
      isConnected: true,
      devMode: true,
      operatingMode: 'AUTONOMOUS',
      currentActivity: 'idle',
      expression: 'happy',
      battery: BatteryStatus(
        percentage: 94.0,
        voltage: 12.4,
        current: 0.45,
        isCharging: false,
        isLow: false,
      ),
      location: Pose2D(x: 0.5, y: 1.2, theta: 0.25),
      unacknowledgedEmergencies: 0,
      nextMedicineReminder: '13:00 - Metformin (500mg)',
      lastHeartbeat: 'Just now',
    );
  }

  static List<Destination> getMockDestinations() {
    return const [
      Destination(id: 'd1', name: 'Living Room', x: 2.5, y: 1.2, theta: 0.0, description: 'Central seating area'),
      Destination(id: 'd2', name: 'Bedroom', x: -1.8, y: 3.4, theta: 1.57, description: 'Patient bedside table'),
      Destination(id: 'd3', name: 'Kitchen', x: 3.2, y: -2.1, theta: -1.57, description: 'Countertop station'),
      Destination(id: 'd4', name: 'Medicine Station', x: 0.5, y: 2.0, theta: 0.78, description: 'Medical supply cabinet'),
      Destination(id: 'd5', name: 'Charging Dock', x: 0.0, y: 0.0, theta: 0.0, description: 'Home recharge station'),
    ];
  }

  static List<MedicineSchedule> getMockMedicines() {
    return [
      MedicineSchedule(
        id: 'med-01',
        name: 'Amlodipine',
        dosage: '5 mg - 1 tablet',
        scheduledTime: '08:00',
        daysOfWeek: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        instructions: 'Take in morning with full glass of water.',
        isActive: true,
        createdAt: DateTime.now().toIso8601String(),
      ),
      MedicineSchedule(
        id: 'med-02',
        name: 'Metformin',
        dosage: '500 mg - 1 tablet',
        scheduledTime: '13:00',
        daysOfWeek: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        instructions: 'Take with midday lunch.',
        isActive: true,
        createdAt: DateTime.now().toIso8601String(),
      ),
      MedicineSchedule(
        id: 'med-03',
        name: 'Atorvastatin',
        dosage: '20 mg - 1 tablet',
        scheduledTime: '20:00',
        daysOfWeek: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        instructions: 'Take before sleep.',
        isActive: true,
        createdAt: DateTime.now().toIso8601String(),
      ),
    ];
  }

  static List<MedicineLogEntry> getMockMedicineLogs() {
    return [
      const MedicineLogEntry(
        id: 'log-1',
        medicineId: 'med-01',
        medicineName: 'Amlodipine',
        dosage: '5 mg',
        scheduledTime: '08:00',
        status: 'taken',
        confirmedBy: 'Patient via Voice',
        confirmedAt: '08:05 AM',
      ),
      const MedicineLogEntry(
        id: 'log-2',
        medicineId: 'med-02',
        medicineName: 'Metformin',
        dosage: '500 mg',
        scheduledTime: '13:00',
        status: 'pending',
      ),
    ];
  }

  static List<EmergencyEvent> getMockEmergencies() {
    return [
      EmergencyEvent(
        eventId: 'em-mock-fall-01',
        eventType: 'fall_confirmed',
        severity: 'CRITICAL',
        timestamp: DateTime.now().subtract(const Duration(minutes: 12)).toIso8601String(),
        confidence: 0.95,
        personName: 'Primary Patient',
        posture: 'lying_down',
        location: const Pose2D(x: 2.1, y: 1.0),
        snapshotUrl: null,
        acknowledged: false,
      ),
    ];
  }

  static List<VoiceInteraction> getMockVoiceHistory() {
    return [
      VoiceInteraction(
        id: 'v1',
        timestamp: DateTime.now().subtract(const Duration(minutes: 25)).toIso8601String(),
        recognizedSpeech: 'Hello LUMI, can you bring my medicine?',
        responseText: 'Hello! I am navigating to the medicine station right now.',
        speaker: 'LUMI',
      ),
      VoiceInteraction(
        id: 'v2',
        timestamp: DateTime.now().subtract(const Duration(minutes: 10)).toIso8601String(),
        recognizedSpeech: 'Thank you LUMI, I have taken it.',
        responseText: 'You are very welcome! I have logged your morning adherence.',
        speaker: 'LUMI',
      ),
    ];
  }

  static List<PersonTrack> getMockPeople() {
    return [
      PersonTrack(
        trackId: 1,
        personName: 'Primary Patient',
        confidence: 0.94,
        posture: 'sitting',
        presenceState: 'PRESENT',
        lastSeenTimestamp: 'Just now',
        bbox: [180, 80, 460, 420],
      ),
    ];
  }

  static List<ActivityTimelineItem> getMockTimeline() {
    return [
      ActivityTimelineItem(
        id: 'act-1',
        timestamp: '10 mins ago',
        category: 'medicine',
        severity: 'INFO',
        title: 'Morning Medicine Taken',
        description: 'Amlodipine (5mg) confirmed taken by patient.',
      ),
      ActivityTimelineItem(
        id: 'act-2',
        timestamp: '25 mins ago',
        category: 'navigation',
        severity: 'INFO',
        title: 'Navigated to Living Room',
        description: 'Autonomous goal succeeded with 0 errors.',
      ),
      ActivityTimelineItem(
        id: 'act-3',
        timestamp: '1 hour ago',
        category: 'system',
        severity: 'INFO',
        title: 'System Health Check OK',
        description: 'Vision, Voice, Base, and Nav2 stacks nominal.',
      ),
    ];
  }
}
