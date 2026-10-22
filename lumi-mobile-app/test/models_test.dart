import 'package:flutter_test/flutter_test.dart';
import 'package:lumi_mobile_app/models/battery_status.dart';
import 'package:lumi_mobile_app/models/destination.dart';
import 'package:lumi_mobile_app/models/emergency_event.dart';
import 'package:lumi_mobile_app/models/medicine.dart';
import 'package:lumi_mobile_app/models/robot_status.dart';
import 'package:lumi_mobile_app/models/voice_interaction.dart';
import 'package:lumi_mobile_app/services/mock_data_service.dart';

void main() {
  group('LUMI Mobile Data Models Unit Tests', () {
    test('BatteryStatus fromJson parses correctly', () {
      final json = {
        'percentage': 88.5,
        'voltage': 12.3,
        'current': 0.6,
        'is_charging': false,
        'is_low': false,
      };
      final batt = BatteryStatus.fromJson(json);
      expect(batt.percentage, 88.5);
      expect(batt.voltage, 12.3);
      expect(batt.isCharging, false);
      expect(batt.isLow, false);
    });

    test('RobotStatus fromJson and toJson roundtrip', () {
      final status = MockDataService.getMockRobotStatus();
      expect(status.robotId, 'lumi-mock-01');
      expect(status.battery.percentage, 94.0);
      expect(status.operatingMode, 'AUTONOMOUS');

      final json = status.toJson();
      expect(json['robot_id'], 'lumi-mock-01');
      expect(json['battery']['percentage'], 94.0);
    });

    test('Destination and NavigationGoal serialization', () {
      final dest = const Destination(
        id: 'd-test',
        name: 'Bedside Table',
        x: 1.2,
        y: -0.5,
        theta: 1.57,
        description: 'Patient room test location',
      );
      final json = dest.toJson();
      expect(json['name'], 'Bedside Table');
      expect(json['x'], 1.2);

      final goal = NavigationGoal.fromJson({
        'goal_id': 'g-1',
        'destination_name': 'Kitchen',
        'target_x': 2.0,
        'target_y': 3.0,
        'status': 'EXECUTING',
        'progress_percent': 45.0,
        'distance_remaining_m': 1.5,
        'estimated_seconds_remaining': 4.0,
      });
      expect(goal.status, 'EXECUTING');
      expect(goal.progressPercent, 45.0);
    });

    test('MedicineSchedule and Log models', () {
      final med = MedicineSchedule.fromJson({
        'id': 'm1',
        'name': 'Amlodipine',
        'dosage': '5mg',
        'scheduled_time': '08:00',
        'days_of_week': ['Mon', 'Tue'],
        'instructions': 'With water',
        'is_active': true,
      });
      expect(med.name, 'Amlodipine');
      expect(med.daysOfWeek.length, 2);

      final log = MedicineLogEntry.fromJson({
        'id': 'l1',
        'medicine_id': 'm1',
        'medicine_name': 'Amlodipine',
        'dosage': '5mg',
        'scheduled_time': '08:00',
        'status': 'taken',
        'confirmed_by': 'Caregiver',
      });
      expect(log.status, 'taken');
      expect(log.confirmedBy, 'Caregiver');
    });

    test('EmergencyEvent fromJson parses confidence and posture', () {
      final ev = EmergencyEvent.fromJson({
        'event_id': 'em-101',
        'event_type': 'fall_confirmed',
        'severity': 'CRITICAL',
        'confidence': 0.98,
        'posture': 'lying_down',
        'person_name': 'Patient John',
        'acknowledged': false,
      });
      expect(ev.eventId, 'em-101');
      expect(ev.confidence, 0.98);
      expect(ev.posture, 'lying_down');
      expect(ev.acknowledged, false);
    });

    test('VoiceInteraction fromJson and AudioDevice', () {
      final vox = VoiceInteraction.fromJson({
        'id': 'v-99',
        'recognized_speech': 'Where are you?',
        'response_text': 'I am near the living room.',
        'speaker': 'LUMI',
      });
      expect(vox.recognizedSpeech, 'Where are you?');
      expect(vox.speaker, 'LUMI');
    });
  });
}
