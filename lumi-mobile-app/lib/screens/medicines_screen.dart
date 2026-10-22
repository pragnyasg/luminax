import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/medicine.dart';
import '../providers/medicine_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class MedicinesScreen extends StatelessWidget {
  const MedicinesScreen({Key? key}) : super(key: key);

  void _showAddMedicineDialog(BuildContext context) {
    final nameCtrl = TextEditingController();
    final dosageCtrl = TextEditingController();
    final timeCtrl = TextEditingController(text: '08:00');
    final notesCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Add Medicine Schedule'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameCtrl,
                decoration: const InputDecoration(labelText: 'Medicine Name', hintText: 'e.g. Amlodipine'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: dosageCtrl,
                decoration: const InputDecoration(labelText: 'Dosage / Quantity', hintText: 'e.g. 5 mg - 1 tablet'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: timeCtrl,
                decoration: const InputDecoration(labelText: 'Scheduled Time (HH:MM)', hintText: 'e.g. 08:00'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: notesCtrl,
                decoration: const InputDecoration(labelText: 'Instructions', hintText: 'e.g. Take with water after breakfast'),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (nameCtrl.text.isNotEmpty && dosageCtrl.text.isNotEmpty) {
                await context.read<MedicineProvider>().addMedicine(
                  name: nameCtrl.text.trim(),
                  dosage: dosageCtrl.text.trim(),
                  scheduledTime: timeCtrl.text.trim(),
                  daysOfWeek: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                  instructions: notesCtrl.text.trim(),
                );
                if (ctx.mounted) Navigator.pop(ctx);
              }
            },
            child: const Text('Save Schedule'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final medProv = context.watch<MedicineProvider>();
    final schedules = medProv.schedules;
    final adherence = medProv.adherence;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Medicine Reminders'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            tooltip: 'Add Medicine',
            onPressed: () => _showAddMedicineDialog(context),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => medProv.loadMedicines(),
        child: ListView(
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            // 1. Adherence Summary Card
            CustomCard(
              backgroundColor: LumiColors.primaryContainer.withOpacity(0.4),
              child: Row(
                children: [
                  Container(
                    width: 54,
                    height: 54,
                    decoration: const BoxDecoration(
                      color: LumiColors.primary,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '${adherence.adherenceRatePercent.toInt()}%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 15,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Patient Adherence Rate',
                          style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${adherence.takenCount} taken on time • ${adherence.skippedCount} skipped • ${adherence.missedCount} missed',
                          style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // 2. Active Schedules Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Daily Prescriptions',
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                  ),
                  TextButton.icon(
                    onPressed: () => _showAddMedicineDialog(context),
                    icon: const Icon(Icons.add, size: 16),
                    label: const Text('Add New'),
                  ),
                ],
              ),
            ),

            if (schedules.isEmpty)
              const Padding(
                padding: EdgeInsets.all(32.0),
                child: Center(
                  child: Text('No active medicine schedules configured.'),
                ),
              ),

            // 3. Schedules List
            ...schedules.map((med) {
              return CustomCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: LumiColors.primaryContainer,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.medication, color: LumiColors.primary, size: 22),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                med.name,
                                style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                              ),
                              Text(
                                med.dosage,
                                style: TextStyle(color: Colors.grey.shade700, fontSize: 13),
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  const Icon(Icons.access_time, size: 13, color: LumiColors.primary),
                                  const SizedBox(width: 4),
                                  Text(
                                    med.scheduledTime,
                                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12, color: LumiColors.primary),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Daily: ${med.daysOfWeek.join(", ")}',
                                    style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
                                  ),
                                ],
                              ),
                              if (med.instructions != null && med.instructions!.isNotEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Text(
                                    med.instructions!,
                                    style: TextStyle(color: Colors.grey.shade600, fontSize: 12, fontStyle: FontStyle.italic),
                                  ),
                                ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.delete_outline, size: 20, color: Colors.grey),
                          tooltip: 'Delete Schedule',
                          onPressed: () => medProv.deleteMedicine(med.id),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    const Divider(height: 1),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        TextButton.icon(
                          onPressed: () => medProv.triggerReminder(med.id),
                          icon: const Icon(Icons.volume_up_outlined, size: 16),
                          label: const Text('Remind Now', style: TextStyle(fontSize: 12)),
                        ),
                        const SizedBox(width: 8),
                        OutlinedButton(
                          onPressed: () => medProv.markAction(med.id, 'skipped', 'Caregiver'),
                          style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6)),
                          child: const Text('Skip', style: TextStyle(fontSize: 12)),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          onPressed: () => medProv.markAction(med.id, 'taken', 'Caregiver'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: LumiColors.success,
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                          ),
                          child: const Text('Mark Taken', style: TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
}
