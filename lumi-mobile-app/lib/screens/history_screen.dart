import 'package:flutter/material.dart';
import '../models/activity_log.dart';
import '../services/mock_data_service.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({Key? key}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  String _selectedCategory = 'all';
  final List<ActivityTimelineItem> _events = MockDataService.getMockTimeline();

  Color _getCategoryColor(String cat) {
    switch (cat.toLowerCase()) {
      case 'emergency':
        return LumiColors.emergency;
      case 'medicine':
        return LumiColors.success;
      case 'navigation':
        return LumiColors.primary;
      case 'voice':
        return LumiColors.info;
      default:
        return Colors.blueGrey;
    }
  }

  IconData _getCategoryIcon(String cat) {
    switch (cat.toLowerCase()) {
      case 'emergency':
        return Icons.warning_rounded;
      case 'medicine':
        return Icons.medication_rounded;
      case 'navigation':
        return Icons.navigation_rounded;
      case 'voice':
        return Icons.record_voice_over_rounded;
      default:
        return Icons.info_outline_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _selectedCategory == 'all'
        ? _events
        : _events.where((e) => e.category.toLowerCase() == _selectedCategory).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Activity & Event History'),
      ),
      body: Column(
        children: [
          // Filter chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: ['all', 'medicine', 'emergency', 'navigation', 'voice', 'system'].map((cat) {
                final isSelected = _selectedCategory == cat;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(cat.toUpperCase()),
                    selected: isSelected,
                    onSelected: (val) {
                      setState(() {
                        _selectedCategory = cat;
                      });
                    },
                  ),
                );
              }).toList(),
            ),
          ),

          // Timeline list
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.only(bottom: 24),
              itemCount: filtered.length,
              itemBuilder: (context, index) {
                final ev = filtered[index];
                final color = _getCategoryColor(ev.category);

                return CustomCard(
                  child: ListTile(
                    leading: Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: color.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(_getCategoryIcon(ev.category), color: color, size: 22),
                    ),
                    title: Text(
                      ev.title,
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(ev.description, style: TextStyle(color: Colors.grey.shade700, fontSize: 12)),
                        const SizedBox(height: 2),
                        Text(ev.timestamp, style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
