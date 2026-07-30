import 'dart:io';
import 'dart:typed_data';
import 'package:path/path.dart' as path;

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'package:record/record.dart';

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
    final directory = Directory.systemTemp;
    final filename = 'medisign_speech_${DateTime.now().millisecondsSinceEpoch}.wav';
    return path.join(directory.path, filename);
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
      final language = _speechService.resolveLanguage(
        voices: _voices,
        selectedVoiceName: _selectedVoiceName,
      );
      final audioBytes = await _speechService.synthesizeSpeech(text: text, language: language);
      await _audioPlayer.play(BytesSource(audioBytes));
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('TTS Error: $error')));
      }
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
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Microphone permission denied')));
      }
      return;
    }
    const config = RecordConfig(
      encoder: AudioEncoder.pcm16bits,
      sampleRate: 16000,
      numChannels: 1,
    );
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
      if (recordedPath == null || recordedPath.isEmpty) {
        throw Exception('No audio recorded');
      }
      final audioBytes = await _readRecordedAudio(recordedPath);
      final language = _speechService.resolveLanguage(
        voices: _voices,
        selectedVoiceName: _selectedVoiceName,
      );
      final transcribedText = await _speechService.transcribeAudio(audioBytes: audioBytes, language: language);
      if (!mounted) return;
      setState(() {
        _sentenceController.text = _sentenceController.text.isEmpty
            ? transcribedText
            : '${_sentenceController.text} $transcribedText';
      });
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Transcription failed: $error')));
      }
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

  Future<Uint8List> _readRecordedAudio(String path) async {
    return (await File(path).readAsBytes());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Speech'), backgroundColor: const Color(0xFF111827)),
      backgroundColor: const Color(0xFF0B1220),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _sentenceController,
            maxLines: 4,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Type text here',
              hintStyle: const TextStyle(color: Colors.white54),
              filled: true,
              fillColor: const Color(0xFF111827),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
          const SizedBox(height: 12),
          if (_isLoadingVoices)
            const LinearProgressIndicator(),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: _selectedVoiceName,
            dropdownColor: const Color(0xFF111827),
            items: _voices
                .map((voice) => DropdownMenuItem(
                      value: voice.name,
                      child: Text(
                        '${voice.shortName} (${voice.genderSymbol} | ${voice.locale})',
                        overflow: TextOverflow.ellipsis,
                      ),
                    ))
                .toList(),
            onChanged: (value) => setState(() => _selectedVoiceName = value),
            decoration: InputDecoration(
              labelText: 'Voice',
              labelStyle: const TextStyle(color: Colors.white70),
              filled: true,
              fillColor: const Color(0xFF111827),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _isSpeaking ? null : _speakText,
                  icon: _isSpeaking
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.volume_up),
                  label: Text(_isSpeaking ? 'Speaking...' : 'Play Speech'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _isTranscribing ? null : _toggleRecording,
                  icon: _isTranscribing
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : Icon(_isRecording ? Icons.stop : Icons.mic),
                  label: Text(_isRecording ? 'Stop & Transcribe' : 'Record Speech'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
