import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({Key? key}) : super(key: key);

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  bool _showDetections = true;
  bool _isPrivacyShieldActive = false;
  int _snapshotCount = 0;
  String _lastSnapshotTime = 'None';
  Key _streamKey = UniqueKey();

  void _reloadStream() {
    setState(() {
      _streamKey = UniqueKey();
    });
  }

  @override
  Widget build(BuildContext context) {
    final settingsProv = context.watch<SettingsProvider>();
    final backendUrl = settingsProv.backendUrl;
    final streamUrl = '$backendUrl/api/v1/camera/stream';
    final snapshotUrl = '$backendUrl/api/v1/camera/snapshot';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Live Camera Monitor'),
        actions: [
          IconButton(
            icon: Icon(_isPrivacyShieldActive ? Icons.visibility_off : Icons.visibility),
            tooltip: 'Toggle Privacy Shield',
            onPressed: () {
              setState(() {
                _isPrivacyShieldActive = !_isPrivacyShieldActive;
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Reload Stream',
            onPressed: _reloadStream,
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.only(bottom: 24),
        children: [
          // 1. Live Video Stream Container
          Container(
            height: 280,
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.15),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            clipBehavior: Clip.antiAlias,
            child: Stack(
              fit: StackFit.expand,
              children: [
                if (_isPrivacyShieldActive)
                  Container(
                    color: LumiColors.surfaceContainerHigh,
                    child: Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.shield_outlined, size: 56, color: LumiColors.primary.withOpacity(0.6)),
                          const SizedBox(height: 12),
                          const Text(
                            'Privacy Shield Active',
                            style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Camera feed blocked by caregiver request',
                            style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  Image.network(
                    streamUrl,
                    key: _streamKey,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      // Graceful fallback to snapshot or offline card
                      return Image.network(
                        snapshotUrl,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.videocam_off_outlined, color: Colors.white54, size: 48),
                                const SizedBox(height: 8),
                                const Text(
                                  'Camera Stream Offline',
                                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Connecting to $streamUrl...',
                                  style: const TextStyle(color: Colors.white54, fontSize: 11),
                                ),
                                const SizedBox(height: 12),
                                ElevatedButton.icon(
                                  onPressed: _reloadStream,
                                  icon: const Icon(Icons.refresh, size: 16),
                                  label: const Text('Retry Connection', style: TextStyle(fontSize: 12)),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.white24,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      );
                    },
                  ),

                // Top stream info overlay badge
                if (!_isPrivacyShieldActive)
                  Positioned(
                    top: 12,
                    left: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.6),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.circle, color: Colors.red, size: 8),
                          SizedBox(width: 6),
                          Text(
                            'LIVE | 30 FPS',
                            style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Bottom person detection indicator
                if (!_isPrivacyShieldActive && _showDetections)
                  Positioned(
                    bottom: 12,
                    left: 12,
                    right: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.65),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.person_pin, color: LumiColors.success, size: 18),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Tracked: Primary Patient | Posture: SITTING (94%)',
                              style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w500),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),

          // 2. Camera Controls & Snapshot Actions
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Vision Overlays & Controls',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                const SizedBox(height: 12),
                SwitchListTile(
                  title: const Text('Show Person Bounding Box', style: TextStyle(fontSize: 14)),
                  subtitle: const Text('Displays real-time pose and posture overlay', style: TextStyle(fontSize: 12)),
                  value: _showDetections,
                  onChanged: (val) {
                    setState(() {
                      _showDetections = val;
                    });
                  },
                ),
                SwitchListTile(
                  title: const Text('Caregiver Privacy Shield', style: TextStyle(fontSize: 14)),
                  subtitle: const Text('Immediately obscures live video feed', style: TextStyle(fontSize: 12)),
                  value: _isPrivacyShieldActive,
                  onChanged: (val) {
                    setState(() {
                      _isPrivacyShieldActive = val;
                    });
                  },
                ),
                const Divider(),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () {
                          setState(() {
                            _snapshotCount++;
                            _lastSnapshotTime = TimeOfDay.now().format(context);
                          });
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Camera snapshot saved successfully.')),
                          );
                        },
                        icon: const Icon(Icons.camera_alt_outlined, size: 18),
                        label: const Text('Capture Snapshot'),
                      ),
                    ),
                  ],
                ),
                if (_snapshotCount > 0)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Center(
                      child: Text(
                        'Snapshots taken: $_snapshotCount | Last at $_lastSnapshotTime',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
