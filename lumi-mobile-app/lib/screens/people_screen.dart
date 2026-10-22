import 'package:flutter/material.dart';
import '../models/person_track.dart';
import '../services/mock_data_service.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class PeopleScreen extends StatelessWidget {
  const PeopleScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final people = MockDataService.getMockPeople();

    return Scaffold(
      appBar: AppBar(
        title: const Text('People & Activity Monitoring'),
      ),
      body: ListView(
        padding: const EdgeInsets.only(bottom: 24),
        children: [
          CustomCard(
            backgroundColor: LumiColors.primaryContainer.withOpacity(0.4),
            child: const Row(
              children: [
                Icon(Icons.face_retouching_natural_outlined, color: LumiColors.primary, size: 28),
                SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'FaceNet & MediaPipe Vision Active',
                        style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                      ),
                      Text(
                        'Continuous posture classification and presence tracking',
                        style: TextStyle(fontSize: 12, color: Colors.black54),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: const Text(
              'Identified Individuals in View',
              style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
            ),
          ),
          ...people.map((person) {
            return CustomCard(
              child: ListTile(
                leading: Container(
                  width: 48,
                  height: 48,
                  decoration: const BoxDecoration(
                    color: LumiColors.primaryContainer,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.person, color: LumiColors.primary, size: 26),
                ),
                title: Text(
                  person.personName ?? 'Unknown Person',
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: LumiColors.successContainer,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            person.presenceState,
                            style: const TextStyle(
                              color: LumiColors.success,
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Posture: ${person.posture.toUpperCase()}',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Confidence: ${(person.confidence * 100).toInt()}% • Last seen: ${person.lastSeenTimestamp}',
                      style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
}
