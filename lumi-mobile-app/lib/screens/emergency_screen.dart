import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/emergency_event.dart';
import '../providers/emergency_provider.dart';
import '../providers/settings_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class EmergencyScreen extends StatelessWidget {
  const EmergencyScreen({Key? key}) : super(key: key);

  void _showAcknowledgeDialog(BuildContext context, EmergencyEvent ev) {
    final noteCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Acknowledge Emergency'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Event ID: ${ev.eventId}'),
            const SizedBox(height: 8),
            Text('Confidence: ${(ev.confidence * 100).toInt()}% | Posture: ${ev.posture}'),
            const SizedBox(height: 12),
            TextField(
              controller: noteCtrl,
              decoration: const InputDecoration(
                labelText: 'Caregiver Note / Action Taken',
                hintText: 'e.g. Checked on patient, helped back to chair',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              await context.read<EmergencyProvider>().acknowledgeEmergency(
                    ev.eventId,
                    'Caregiver',
                    note: noteCtrl.text.trim(),
                  );
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: const Text('Confirm Acknowledged'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final emergencyProv = context.watch<EmergencyProvider>();
    final settingsProv = context.watch<SettingsProvider>();
    final emergencies = emergencyProv.emergencies;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergency & Fall Events'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_alert_outlined),
            tooltip: 'Simulate Fall',
            onPressed: () async {
              await emergencyProv.simulateFall();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Simulated fall alert created.')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: () => emergencyProv.loadEmergencies(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => emergencyProv.loadEmergencies(),
        child: ListView(
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            // Status overview
            CustomCard(
              backgroundColor: emergencyProv.hasActiveEmergency
                  ? LumiColors.emergencyContainer
                  : LumiColors.successContainer,
              child: Row(
                children: [
                  Icon(
                    emergencyProv.hasActiveEmergency ? Icons.warning_rounded : Icons.verified_user_outlined,
                    color: emergencyProv.hasActiveEmergency ? LumiColors.emergency : LumiColors.success,
                    size: 32,
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          emergencyProv.hasActiveEmergency
                              ? '${emergencyProv.unacknowledged.length} UNACKNOWLEDGED ALERTS'
                              : 'No Active Emergencies',
                          style: TextStyle(
                            fontWeight: FontWeight.w800,
                            fontSize: 14,
                            color: emergencyProv.hasActiveEmergency ? LumiColors.emergency : LumiColors.success,
                          ),
                        ),
                        Text(
                          emergencyProv.hasActiveEmergency
                              ? 'Immediate caregiver verification recommended'
                              : 'Computer vision fall detector and safety monitor nominal',
                          style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
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
                'Incident Timeline',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
              ),
            ),

            if (emergencies.isEmpty)
              const Padding(
                padding: EdgeInsets.all(32.0),
                child: Center(child: Text('No emergency events on record.')),
              ),

            ...emergencies.map((ev) {
              final isUnack = !ev.acknowledged;

              return CustomCard(
                backgroundColor: isUnack ? LumiColors.emergencyContainer.withOpacity(0.5) : null,
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
                            color: isUnack ? LumiColors.emergency : Colors.grey.shade300,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            Icons.personal_injury_outlined,
                            color: isUnack ? Colors.white : Colors.black54,
                            size: 24,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    ev.eventType.replaceAll('_', ' ').toUpperCase(),
                                    style: TextStyle(
                                      fontWeight: FontWeight.w800,
                                      fontSize: 14,
                                      color: isUnack ? LumiColors.emergency : Colors.black87,
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: isUnack ? LumiColors.emergency : Colors.grey.shade200,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      isUnack ? 'ACTION REQUIRED' : 'RESOLVED',
                                      style: TextStyle(
                                        color: isUnack ? Colors.white : Colors.black54,
                                        fontSize: 9,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Confidence: ${(ev.confidence * 100).toInt()}% | Posture: ${ev.posture.replaceAll('_', ' ').toUpperCase()}',
                                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12),
                              ),
                              Text(
                                'Time: ${ev.timestamp.split("T").join(" ").split(".").first}',
                                style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
                              ),
                              if (ev.resolutionNotes != null)
                                Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Text(
                                    'Resolution: ${ev.resolutionNotes}',
                                    style: TextStyle(color: Colors.grey.shade700, fontSize: 12, fontStyle: FontStyle.italic),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    if (isUnack) ...[
                      const SizedBox(height: 12),
                      const Divider(height: 1),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          OutlinedButton.icon(
                            onPressed: () => emergencyProv.callResponder(
                              ev.eventId,
                              phone: settingsProv.settings.caregiverPhone,
                            ),
                            icon: const Icon(Icons.phone, size: 16),
                            label: const Text('Call Responder', style: TextStyle(fontSize: 12)),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton.icon(
                            onPressed: () => _showAcknowledgeDialog(context, ev),
                            icon: const Icon(Icons.check, size: 16),
                            label: const Text('Acknowledge', style: TextStyle(fontSize: 12)),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: LumiColors.emergency,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ],
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
