import 'package:flutter/foundation.dart';
import '../models/voice_interaction.dart';
import '../services/api_service.dart';
import '../services/mock_data_service.dart';

class VoiceProvider with ChangeNotifier {
  final ApiService _apiService;
  bool _useMockMode = false;

  List<VoiceInteraction> _history = [];
  bool _isProcessing = false;
  String? _errorMessage;

  List<VoiceInteraction> get history => _history;
  bool get isProcessing => _isProcessing;
  String? get errorMessage => _errorMessage;

  VoiceProvider({required ApiService apiService}) : _apiService = apiService;

  void updateConfig({required bool useMockMode}) {
    _useMockMode = useMockMode;
    loadHistory();
  }

  Future<void> loadHistory() async {
    _history = MockDataService.getMockVoiceHistory();
    notifyListeners();
  }

  Future<bool> sendCommand(String command) async {
    _isProcessing = true;
    _errorMessage = null;
    notifyListeners();

    if (_useMockMode) {
      await Future.delayed(const Duration(milliseconds: 600));
      _history.insert(0, VoiceInteraction(
        id: 'vox-sim-${DateTime.now().millisecondsSinceEpoch}',
        timestamp: DateTime.now().toIso8601String(),
        recognizedSpeech: command,
        responseText: 'I received your command: "$command". Executing coordinated health task.',
        speaker: 'LUMI',
      ));
      _isProcessing = false;
      notifyListeners();
      return true;
    }

    try {
      final interaction = await _apiService.sendVoiceCommand(command);
      _history.insert(0, interaction);
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      return false;
    } finally {
      _isProcessing = false;
      notifyListeners();
    }
  }

  Future<bool> speakPhrase(String phrase) async {
    if (_useMockMode) return true;
    return await _apiService.speakPhrase(phrase);
  }
}
