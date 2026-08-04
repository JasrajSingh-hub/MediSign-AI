import 'dart:io';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:path/path.dart' as path;

import '../data/speech_backend_service.dart';

class SpeechScreen extends StatefulWidget {
  const SpeechScreen({super.key});

  @override
  State<SpeechScreen> createState() => _SpeechScreenState();
}

class _SpeechScreenState extends State<SpeechScreen> {
  final SpeechBackendService _speechService = const SpeechBackendService();
  final AudioPlayer _audioPlayer = AudioPlayer();
  final AudioRecorder _audioRecorder = AudioRecorder();
  final TextEditingController _sentenceController = TextEditingController();

  List<VoiceOption> _voices = [];
  String? _selectedVoiceName;
  bool _isLoadingVoices = false;
  bool _isSpeaking = false;
  bool _isRecording = false;
  bool _isTranscribing = false;
  String? _recordingPath;

  @override
  void initState() {
    super.initState();
    _loadVoices();
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    _audioRecorder.dispose();
    _sentenceController.dispose();
    super.dispose();
  }

  String _createRecordingPath() {
    final filename = 'medisign_speech_${DateTime.now().millisecondsSinceEpoch}.wav';
    return path.join(Directory.systemTemp.path, filename);
  }

  Future<void> _loadVoices() async {
    setState(() => _isLoadingVoices = true);
    try {
      final voices = await _speechService.fetchVoices();
      if (!mounted) return;
      setState(() {
        _voices = voices;
        _selectedVoiceName ??= voices.isNotEmpty ? _speechService.resolvePreferredVoiceName(voices) : null;
      });
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to load voices')));
      }
    } finally {
      if (mounted) setState(() => _isLoadingVoices = false);
    }
  }

  Future<void> _speakText() async {
    final text = _sentenceController.text.trim();
    if (text.isEmpty) return;
    setState(() => _isSpeaking = true);
    try {
      final language = _speechService.resolveLanguage(voices: _voices, selectedVoiceName: _selectedVoiceName);
      final audioBytes = await _speechService.synthesizeSpeech(text: text, language: language);
      await _audioPlayer.play(BytesSource(audioBytes));
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('TTS Error: $error')));
    } finally {
      if (mounted) setState(() => _isSpeaking = false);
    }
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      await _stopRecordingAndTranscribe();
    } else {
      await _startRecording();
    }
  }

  Future<void> _startRecording() async {
    if (!await _audioRecorder.hasPermission()) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Microphone permission denied')));
      return;
    }
    const config = RecordConfig(encoder: AudioEncoder.pcm16bits, sampleRate: 16000, numChannels: 1);
    final recordingPath = _createRecordingPath();
    await _audioRecorder.start(config, path: recordingPath);
    if (!mounted) return;
    setState(() {
      _isRecording = true;
      _recordingPath = recordingPath;
    });
  }

  Future<void> _stopRecordingAndTranscribe() async {
    setState(() {
      _isRecording = false;
      _isTranscribing = true;
    });
    try {
      final recordedPath = await _audioRecorder.stop() ?? _recordingPath;
      if (recordedPath == null || recordedPath.isEmpty) throw Exception('No audio recorded');
      final audioBytes = await _readRecordedAudio(recordedPath);
      final language = _speechService.resolveLanguage(voices: _voices, selectedVoiceName: _selectedVoiceName);
      final transcribedText = await _speechService.transcribeAudio(audioBytes: audioBytes, language: language);
      if (!mounted) return;
      setState(() {
        _sentenceController.text = _sentenceController.text.isEmpty ? transcribedText : '${_sentenceController.text} $transcribedText';
      });
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Transcription failed: $error')));
    } finally {
      final recordedPath = _recordingPath;
      if (recordedPath != null) {
        try {
          await File(recordedPath).delete();
        } catch (_) {}
      }
      _recordingPath = null;
      if (mounted) setState(() => _isTranscribing = false);
    }
  }

  Future<Uint8List> _readRecordedAudio(String path) async => File(path).readAsBytes();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Vocalizer')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _Panel(
              title: 'Speech Synthesis',
              subtitle: 'Type a message or capture speech, then play it back.',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    controller: _sentenceController,
                    maxLines: 5,
                    decoration: const InputDecoration(hintText: 'Type or speak a message...'),
                  ),
                  const SizedBox(height: 12),
                  if (_isLoadingVoices) const LinearProgressIndicator(),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _selectedVoiceName,
                    dropdownColor: const Color(0xFF122031),
                    items: _voices
                        .map(
                          (voice) => DropdownMenuItem(
                            value: voice.name,
                            child: Text('${voice.shortName} (${voice.genderSymbol} | ${voice.locale})', overflow: TextOverflow.ellipsis),
                          ),
                        )
                        .toList(),
                    onChanged: (value) => setState(() => _selectedVoiceName = value),
                    decoration: const InputDecoration(labelText: 'Voice'),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: _isSpeaking ? null : _speakText,
                          icon: _isSpeaking
                              ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                              : const Icon(Icons.volume_up),
                          label: Text(_isSpeaking ? 'Speaking...' : 'Play Speech'),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _isTranscribing ? null : _toggleRecording,
                          icon: _isTranscribing
                              ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                              : Icon(_isRecording ? Icons.stop : Icons.mic),
                          label: Text(_isRecording ? 'Stop & Transcribe' : 'Record Speech'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _Panel(
              title: 'Recent Transcriptions',
              child: const Text(
                'Use the mic to capture speech or the play button to speak typed text.',
                style: TextStyle(color: Color(0xFFBBC9CD)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Panel extends StatelessWidget {
  const _Panel({required this.title, required this.child, this.subtitle});

  final String title;
  final String? subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF122031),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: Color(0xFFD5E4FA), fontSize: 18, fontWeight: FontWeight.w700)),
          if (subtitle != null) ...[
            const SizedBox(height: 6),
            Text(subtitle!, style: const TextStyle(color: Color(0xFFBBC9CD), fontSize: 13)),
          ],
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }
}
