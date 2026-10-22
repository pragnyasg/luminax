import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/voice_provider.dart';
import '../theme/lumi_colors.dart';
import '../widgets/custom_card.dart';

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({Key? key}) : super(key: key);

  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  final TextEditingController _cmdCtrl = TextEditingController();

  void _submitCommand() {
    final text = _cmdCtrl.text.trim();
    if (text.isNotEmpty) {
      context.read<VoiceProvider>().sendCommand(text);
      _cmdCtrl.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    final voiceProv = context.watch<VoiceProvider>();
    final history = voiceProv.history;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice & Speech Interaction'),
        actions: [
          IconButton(
            icon: const Icon(Icons.volume_up_outlined),
            tooltip: 'Audio Test',
            onPressed: () {
              voiceProv.speakPhrase('LUMI audio output test nominal.');
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Audio test phrase dispatched to robot speaker.')),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Speech state banner
          CustomCard(
            backgroundColor: LumiColors.infoContainer.withOpacity(0.4),
            child: Row(
              children: [
                const Icon(Icons.graphic_eq_rounded, color: LumiColors.info, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Voice Pipeline Active',
                        style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                      ),
                      Text(
                        voiceProv.isProcessing ? 'Processing request with Ollama...' : 'Whisper STT & Piper TTS online',
                        style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                if (voiceProv.isProcessing)
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
              ],
            ),
          ),

          // Conversation bubbles list
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              reverse: false,
              itemCount: history.length,
              itemBuilder: (context, index) {
                final item = history[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // User Recognized Speech
                      Align(
                        alignment: Alignment.centerRight,
                        child: Container(
                          constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          decoration: BoxDecoration(
                            color: LumiColors.primary,
                            borderRadius: const BorderRadius.only(
                              topLeft: Radius.circular(16),
                              topRight: Radius.circular(16),
                              bottomLeft: Radius.circular(16),
                              bottomRight: Radius.circular(4),
                            ),
                          ),
                          child: Text(
                            item.recognizedSpeech,
                            style: const TextStyle(color: Colors.white, fontSize: 14),
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      // LUMI Response
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Container(
                          constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          decoration: BoxDecoration(
                            color: LumiColors.surfaceContainer,
                            borderRadius: const BorderRadius.only(
                              topLeft: Radius.circular(16),
                              topRight: Radius.circular(16),
                              bottomRight: Radius.circular(16),
                              bottomLeft: Radius.circular(4),
                            ),
                            border: Border.all(color: Colors.black.withOpacity(0.05)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.responseText,
                                style: const TextStyle(color: Colors.black87, fontSize: 14),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${item.speaker} • ${item.source}',
                                style: TextStyle(color: Colors.grey.shade500, fontSize: 10),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),

          // Command input bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: LumiColors.surface,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.04),
                  blurRadius: 8,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _cmdCtrl,
                    onSubmitted: (_) => _submitCommand(),
                    decoration: InputDecoration(
                      hintText: 'Send text command to LUMI...',
                      filled: true,
                      fillColor: LumiColors.surfaceContainer,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _submitCommand,
                  icon: const Icon(Icons.send_rounded),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
