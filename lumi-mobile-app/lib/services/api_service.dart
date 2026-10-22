import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/robot_status.dart';
import '../models/battery_status.dart';
import '../models/destination.dart';
import '../models/medicine.dart';
import '../models/emergency_event.dart';
import '../models/voice_interaction.dart';
import '../models/person_track.dart';
import '../models/activity_log.dart';

class ApiService {
  String baseUrl;
  String? apiKey;

  ApiService({
    this.baseUrl = 'http://192.168.1.100:8000',
    this.apiKey,
  });

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    if (apiKey != null && apiKey!.isNotEmpty) 'X-API-Key': apiKey!,
  };

  // 1. Robot Status & Diagnostics
  Future<RobotStatus> fetchRobotStatus() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/robot/status'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      return RobotStatus.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Failed to load status (${res.statusCode})');
  }

  Future<BatteryStatus> fetchBattery() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/robot/battery'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      return BatteryStatus.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Failed to load battery (${res.statusCode})');
  }

  // 2. Navigation
  Future<List<Destination>> fetchDestinations() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/navigation/destinations'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      final List list = jsonDecode(res.body) as List;
      return list.map((e) => Destination.fromJson(e as Map<String, dynamic>)).toList();
    }
    throw Exception('Failed to load destinations (${res.statusCode})');
  }

  Future<NavigationGoal> fetchCurrentGoal() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/navigation/goals'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      return NavigationGoal.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Failed to load goal (${res.statusCode})');
  }

  Future<NavigationGoal> dispatchGoal({String? destinationId, double? x, double? y, double theta = 0.0}) async {
    final body = jsonEncode({
      if (destinationId != null) 'destination_id': destinationId,
      if (x != null) 'x': x,
      if (y != null) 'y': y,
      'theta': theta,
    });
    final res = await http.post(Uri.parse('$baseUrl/api/v1/navigation/goals'), headers: _headers, body: body).timeout(const Duration(seconds: 5));
    if (res.statusCode == 200) {
      return NavigationGoal.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Failed to dispatch navigation goal (${res.statusCode})');
  }

  Future<bool> cancelGoal() async {
    final res = await http.post(Uri.parse('$baseUrl/api/v1/navigation/cancel'), headers: _headers).timeout(const Duration(seconds: 4));
    return res.statusCode == 200;
  }

  // 3. Medicines
  Future<List<MedicineSchedule>> fetchMedicines() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/medicines'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      final List list = jsonDecode(res.body) as List;
      return list.map((e) => MedicineSchedule.fromJson(e as Map<String, dynamic>)).toList();
    }
    throw Exception('Failed to load medicines (${res.statusCode})');
  }

  Future<MedicineSchedule> createMedicine(Map<String, dynamic> data) async {
    final res = await http.post(Uri.parse('$baseUrl/api/v1/medicines'), headers: _headers, body: jsonEncode(data)).timeout(const Duration(seconds: 5));
    if (res.statusCode == 201) {
      return MedicineSchedule.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Failed to create medicine (${res.statusCode})');
  }

  Future<bool> deleteMedicine(String id) async {
    final res = await http.delete(Uri.parse('$baseUrl/api/v1/medicines/$id'), headers: _headers).timeout(const Duration(seconds: 4));
    return res.statusCode == 200;
  }

  Future<bool> triggerMedicineReminder(String id) async {
    final res = await http.post(Uri.parse('$baseUrl/api/v1/medicines/$id/trigger'), headers: _headers).timeout(const Duration(seconds: 4));
    return res.statusCode == 200;
  }

  Future<bool> recordMedicineAction(String id, String action, String confirmedBy) async {
    final body = jsonEncode({'action': action, 'confirmed_by': confirmedBy});
    final res = await http.post(Uri.parse('$baseUrl/api/v1/medicines/$id/action'), headers: _headers, body: body).timeout(const Duration(seconds: 4));
    return res.statusCode == 200;
  }

  Future<AdherenceSummary> fetchAdherenceSummary() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/medicines/adherence/summary'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      return AdherenceSummary.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    return const AdherenceSummary(totalDoses: 0, takenCount: 0, skippedCount: 0, missedCount: 0, adherenceRatePercent: 100.0);
  }

  // 4. Emergencies
  Future<List<EmergencyEvent>> fetchEmergencies({bool unacknowledgedOnly = false}) async {
    final url = '$baseUrl/api/v1/emergencies${unacknowledgedOnly ? "?unacknowledged_only=true" : ""}';
    final res = await http.get(Uri.parse(url), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      final List list = jsonDecode(res.body) as List;
      return list.map((e) => EmergencyEvent.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  Future<bool> acknowledgeEmergency(String eventId, String acknowledgedBy, {String? note}) async {
    final body = jsonEncode({'acknowledged_by': acknowledgedBy, 'note': note});
    final res = await http.post(Uri.parse('$baseUrl/api/v1/emergencies/$eventId/acknowledge'), headers: _headers, body: body).timeout(const Duration(seconds: 4));
    return res.statusCode == 200;
  }

  Future<bool> callEmergencyResponder(String eventId, {String? phone}) async {
    final body = jsonEncode({'responder_phone': phone});
    final res = await http.post(Uri.parse('$baseUrl/api/v1/emergencies/$eventId/call'), headers: _headers, body: body).timeout(const Duration(seconds: 4));
    return res.statusCode == 200;
  }

  Future<EmergencyEvent?> simulateFallAlert() async {
    final res = await http.post(Uri.parse('$baseUrl/api/v1/emergencies/simulate_fall'), headers: _headers).timeout(const Duration(seconds: 5));
    if (res.statusCode == 200) {
      return EmergencyEvent.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    return null;
  }

  // 5. Manual Controls
  Future<bool> sendManualControl(double linearX, double angularZ, {bool safetyOverride = false}) async {
    final body = jsonEncode({
      'linear_x': linearX,
      'angular_z': angularZ,
      'enable_safety_override': safetyOverride,
    });
    final res = await http.post(Uri.parse('$baseUrl/api/v1/control/manual'), headers: _headers, body: body).timeout(const Duration(seconds: 2));
    return res.statusCode == 200;
  }

  Future<bool> sendStop() async {
    final res = await http.post(Uri.parse('$baseUrl/api/v1/control/stop'), headers: _headers).timeout(const Duration(seconds: 2));
    return res.statusCode == 200;
  }

  // 6. Voice
  Future<VoiceInteraction> sendVoiceCommand(String command) async {
    final body = jsonEncode({'command': command});
    final res = await http.post(Uri.parse('$baseUrl/api/v1/voice/command'), headers: _headers, body: body).timeout(const Duration(seconds: 5));
    if (res.statusCode == 200) {
      return VoiceInteraction.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Failed to send voice command');
  }

  Future<bool> speakPhrase(String phrase) async {
    final body = jsonEncode({'phrase': phrase});
    final res = await http.post(Uri.parse('$baseUrl/api/v1/voice/speak'), headers: _headers, body: body).timeout(const Duration(seconds: 4));
    return res.statusCode == 200;
  }

  // 7. People & Activity
  Future<List<PersonTrack>> fetchPeople() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/people'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      final List list = jsonDecode(res.body) as List;
      return list.map((e) => PersonTrack.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  Future<List<ActivityTimelineItem>> fetchActivityHistory() async {
    final res = await http.get(Uri.parse('$baseUrl/api/v1/events'), headers: _headers).timeout(const Duration(seconds: 4));
    if (res.statusCode == 200) {
      final List list = jsonDecode(res.body) as List;
      return list.map((e) => ActivityTimelineItem.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }
}
