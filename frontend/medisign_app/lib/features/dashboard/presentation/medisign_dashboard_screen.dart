import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:record/record.dart';
import 'package:path/path.dart' as path;

import '../../../core/utils/web_camera_helper.dart';
import '../../avatar/data/avatar_backend_service.dart';
import '../../avatar/presentation/avatar_pose_painter.dart';
import '../../sign_detection/data/sign_detection_service.dart';
import '../../speech/data/speech_backend_service.dart';

class MediSignDashboardScreen extends StatefulWidget {
  const MediSignDashboardScreen({
    super.key,
    required this.availableCameras,
  });

  final List<CameraDescription> availableCameras;

  @override
  State<MediSignDashboardScreen> createState() => _MediSignDashboardScreenState();
}

class _MediSignDashboardScreenState extends State<MediSignDashboardScreen> {
  final SpeechBackendService _speechService = const SpeechBackendService();
  final SignDetectionService _signDetectionService = const SignDetectionService();
  final AvatarBackendService _avatarService = const AvatarBackendService();

  final AudioPlayer _audioPlayer = AudioPlayer();
  final AudioRecorder _audioRecorder = AudioRecorder();
  final TextEditingController _sentenceController = TextEditingController();

  CameraController? _cameraController;
  Timer? _frameProcessingTimer;
  Timer? _avatarAnimationTimer;

  bool _isCameraInitialized = false;
  bool _isProcessingFrame = false;
  String? _cameraError;

  String _predictionText = 'Waiting for clinician sign language input...';
  String _currentPredictedLetter = '';

  List<VoiceOption> _voices = [];
  String? _selectedVoiceName;
  bool _isLoadingVoices = false;
  bool _isSpeaking = false;

  bool _isRecording = false;
  bool _isTranscribing = false;
  String? _recordingPath;

  Map<String, dynamic> _avatarLibrary = {};
  Map<String, dynamic> _currentAvatarJoints = {};
  List<String> _activeAvatarTokens = [];
  int _currentAvatarTokenIndex = 0;
  String _currentAvatarToken = '';
  bool _isPlayingAvatar = false;
  bool _isLoadingAvatarLibrary = false;
  bool _isParsingAvatarText = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _loadVoices();
    _loadAvatarLibrary();
  }

  @override
  void dispose() {
    _frameProcessingTimer?.cancel();
    _avatarAnimationTimer?.cancel();
    _cameraController?.dispose();
    _sentenceController.dispose();
    _audioPlayer.dispose();
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _initializeCamera() async {
    if (mounted) {
      setState(() {
        _cameraError = null;
      });
    }

    String? permError;
    if (kIsWeb) {
      try {
        await requestWebCameraPermission();
      } catch (e) {
        permError = '$e';
      }
    }

    List<CameraDescription> cameras = widget.availableCameras;
    try {
      cameras = await availableCameras();
    } catch (error) {
      debugPrint('Error finding cameras dynamically: $error');
      permError = '$error';
    }

    if (cameras.isEmpty) {
      if (mounted) {
        setState(() {
          _cameraError = 'No camera device found (count: 0).' +
              (permError != null ? ' Details: $permError' : ' Please ensure your webcam is connected & allowed in Chrome.');
          _isCameraInitialized = false;
        });
      }
      return;
    }

    final controller = CameraController(
      cameras.first,
      ResolutionPreset.low,
      enableAudio: false,
    );

    try {
      await controller.initialize();
      if (!mounted) {
        await controller.dispose();
        return;
      }

      setState(() {
        _cameraController = controller;
        _isCameraInitialized = true;
        _cameraError = null;
      });

      _frameProcessingTimer?.cancel();
      _frameProcessingTimer = Timer.periodic(
        const Duration(milliseconds: 300),
        (_) => _processCameraFrame(),
      );
    } catch (error) {
      debugPrint('Camera hardware configuration error: $error');
      try {
        await controller.dispose();
      } catch (_) {}
      if (mounted) {
        setState(() {
          _cameraError = 'Camera init failed: $error';
          _isCameraInitialized = false;
        });
      }
    }
  }

  Future<void> _openEmergencyScreen() async {
    _frameProcessingTimer?.cancel();
    _frameProcessingTimer = null;

    final controller = _cameraController;
    _cameraController = null;
    _isCameraInitialized = false;

    if (controller != null) {
      try {
        await controller.dispose();
      } catch (error) {
        debugPrint('Error disposing dashboard camera: $error');
      }
    }

    if (!mounted) {
      return;
    }

    await Navigator.of(context).pushNamed('/emergency');

    if (!mounted) {
      return;
    }

    await _initializeCamera();
  }

  Future<void> _processCameraFrame() async {
    final controller = _cameraController;
    if (_isProcessingFrame ||
        controller == null ||
        !controller.value.isInitialized ||
        controller.value.isTakingPicture) {
      return;
    }

    setState(() {
      _isProcessingFrame = true;
    });

    try {
      final pictureFile = await controller.takePicture();
      final imageBytes = await pictureFile.readAsBytes();

      final prediction = await _signDetectionService.predictFromImageBytes(imageBytes);
      if (!mounted || prediction == null) {
        return;
      }

      setState(() {
        _predictionText = prediction.displayText;
        _currentPredictedLetter = prediction.letter;
      });
    } catch (_) {
      // Ignore intermittent frame or backend failures so the preview stays responsive.
    } finally {
      if (mounted) {
        setState(() {
          _isProcessingFrame = false;
        });
      }
    }
  }

  Future<void> _loadVoices() async {
    setState(() {
      _isLoadingVoices = true;
    });

    try {
      final voices = await _speechService.fetchVoices();
      if (!mounted) {
        return;
      }

      setState(() {
        _voices = voices;
        if (_selectedVoiceName == null && voices.isNotEmpty) {
          _selectedVoiceName = _speechService.resolvePreferredVoiceName(voices);
        }
      });
    } catch (error) {
      debugPrint('Failed to fetch voices from TTS service: $error');
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingVoices = false;
        });
      }
    }
  }

  Future<void> _speakText() async {
    final text = _sentenceController.text.trim();
    if (text.isEmpty) {
      return;
    }

    setState(() {
      _isSpeaking = true;
    });

    try {
      final language = _speechService.resolveLanguage(
        voices: _voices,
        selectedVoiceName: _selectedVoiceName,
      );
      final audioBytes = await _speechService.synthesizeSpeech(
        text: text,
        language: language,
      );
      await _audioPlayer.play(BytesSource(audioBytes));
    } catch (error) {
      debugPrint('Error calling TTS speak API: $error');
      _showSnackBar('TTS Error: $error');
    } finally {
      if (mounted) {
        setState(() {
          _isSpeaking = false;
        });
      }
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
    try {
      if (!await _audioRecorder.hasPermission()) {
        _showSnackBar('Microphone permission denied');
        return;
      }

      const config = RecordConfig(
        encoder: AudioEncoder.pcm16bits,
        sampleRate: 16000,
        numChannels: 1,
      );

      final recordingPath = path.join(
        Directory.systemTemp.path,
        'medisign_dashboard_${DateTime.now().millisecondsSinceEpoch}.wav',
      );
      await _audioRecorder.start(config, path: recordingPath);
      if (!mounted) {
        return;
      }

      setState(() {
        _isRecording = true;
        _recordingPath = recordingPath;
      });
    } catch (error) {
      debugPrint('Error starting recording: $error');
      _showSnackBar('Failed to start recording: $error');
    }
  }

  Future<void> _stopRecordingAndTranscribe() async {
    try {
      setState(() {
        _isRecording = false;
        _isTranscribing = true;
      });

      final recordedPath = await _audioRecorder.stop() ?? _recordingPath;
      if (recordedPath == null || recordedPath.isEmpty) {
        throw Exception('No audio recorded');
      }

      final audioBytes = await _readRecordedAudio(recordedPath);
      final language = _speechService.resolveLanguage(
        voices: _voices,
        selectedVoiceName: _selectedVoiceName,
      );
      final transcribedText = await _speechService.transcribeAudio(
        audioBytes: audioBytes,
        language: language,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        if (_sentenceController.text.isEmpty) {
          _sentenceController.text = transcribedText;
        } else {
          _sentenceController.text += ' $transcribedText';
        }
      });
    } catch (error) {
      debugPrint('Error stopping recording or transcribing: $error');
      _showSnackBar('Transcription failed: $error');
    } finally {
      final recordedPath = _recordingPath;
      if (recordedPath != null) {
        try {
          await File(recordedPath).delete();
        } catch (_) {}
      }
      _recordingPath = null;
      if (mounted) {
        setState(() {
          _isTranscribing = false;
        });
      }
    }
  }

  Future<Uint8List> _readRecordedAudio(String path) async {
    if (kIsWeb) {
      final response = await http.get(Uri.parse(path));
      return response.bodyBytes;
    }

    return File(path).readAsBytes();
  }

  Future<void> _loadAvatarLibrary() async {
    setState(() {
      _isLoadingAvatarLibrary = true;
    });

    try {
      final library = await _avatarService.loadCoordinateLibrary();
      if (!mounted) {
        return;
      }

      setState(() {
        _avatarLibrary = library;
      });
    } catch (error) {
      debugPrint('Error loading avatar library: $error');
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingAvatarLibrary = false;
        });
      }
    }
  }

  Future<void> _parseAvatarTextAndPlay() async {
    final text = _sentenceController.text.trim();
    if (text.isEmpty) {
      return;
    }

    setState(() {
      _isParsingAvatarText = true;
      _isPlayingAvatar = false;
      _currentAvatarToken = '';
      _avatarAnimationTimer?.cancel();
      _currentAvatarJoints = {};
      _activeAvatarTokens = [];
      _currentAvatarTokenIndex = 0;
    });

    try {
      final tokens = await _avatarService.parseTokens(text);
      if (!mounted) {
        return;
      }

      setState(() {
        _activeAvatarTokens = tokens;
      });

      if (tokens.isEmpty) {
        _showSnackBar('No sign tokens were returned for this text.');
        return;
      }

      _startAvatarAnimationLoop();
    } catch (error) {
      _showSnackBar('$error. Check the backend route.');
    } finally {
      if (mounted) {
        setState(() {
          _isParsingAvatarText = false;
        });
      }
    }
  }

  void _startAvatarAnimationLoop() {
    setState(() {
      _isPlayingAvatar = true;
      _currentAvatarTokenIndex = 0;
    });

    _showAvatarToken(_activeAvatarTokens[_currentAvatarTokenIndex]);

    _avatarAnimationTimer = Timer.periodic(
      const Duration(milliseconds: 750),
      (timer) {
        _currentAvatarTokenIndex++;

        if (_currentAvatarTokenIndex >= _activeAvatarTokens.length) {
          timer.cancel();
          if (!mounted) {
            return;
          }

          setState(() {
            _isPlayingAvatar = false;
            _currentAvatarToken = '';
            _currentAvatarJoints = {};
          });
          return;
        }

        _showAvatarToken(_activeAvatarTokens[_currentAvatarTokenIndex]);
      },
    );
  }

  void _showAvatarToken(String token) {
    final normalizedToken = token.trim().toUpperCase();
    if (!mounted) {
      return;
    }

    if (normalizedToken.isEmpty || normalizedToken == 'SPACE') {
      setState(() {
        _currentAvatarToken = 'Pause';
        _currentAvatarJoints = {};
      });
      return;
    }

final entry = _avatarLibrary[normalizedToken];

if (entry is List && entry.isNotEmpty) {
  final firstFrame = entry.first;

  if (firstFrame is Map) {
    setState(() {
      _currentAvatarToken = normalizedToken;
      _currentAvatarJoints = Map<String, dynamic>.from(firstFrame);
    });
    return;
  }
}

    setState(() {
      _currentAvatarToken = '$normalizedToken (missing)';
      _currentAvatarJoints = {};
    });
  }

  void _appendDetectedLetter() {
    setState(() {
      _sentenceController.text += _currentPredictedLetter;
    });
  }

  void _appendSpace() {
    setState(() {
      _sentenceController.text += ' ';
    });
  }

  void _removeLastCharacter() {
    final currentText = _sentenceController.text;
    if (currentText.isEmpty) {
      return;
    }

    setState(() {
      _sentenceController.text = currentText.substring(0, currentText.length - 1);
    });
  }

  void _clearSentence() {
    setState(() {
      _sentenceController.clear();
    });
  }

  void _showSnackBar(String message) {
    if (!mounted) {
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openEmergencyScreen,
        backgroundColor: Colors.redAccent,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.warning_amber_rounded),
        label: const Text('Emergency AI'),
      ),
      persistentFooterButtons: [
        TextButton.icon(
          onPressed: () => Navigator.of(context).pushNamed('/prescription'),
          icon: const Icon(Icons.medical_services, color: Colors.cyanAccent),
          label: const Text('Prescription', style: TextStyle(color: Colors.cyanAccent)),
        ),
      ],
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              flex: 4,
              child: _buildCameraPanel(),
            ),
            Expanded(
              flex: 5,
              child: SingleChildScrollView(
                child: _buildWorkspacePanel(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCameraPanel() {
    return Container(
      margin: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      width: double.infinity,
      child: _isCameraInitialized && _cameraController != null
          ? ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: CameraPreview(_cameraController!),
            )
          : Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (_cameraError != null) ...[
                      const Icon(Icons.videocam_off_rounded, color: Colors.amberAccent, size: 48),
                      const SizedBox(height: 12),
                      Text(
                        _cameraError!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Color(0xFFD5E4FA), fontSize: 14),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _initializeCamera,
                        icon: const Icon(Icons.videocam),
                        label: const Text('Enable / Allow Camera Access'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0284C7),
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ] else ...[
                      const CircularProgressIndicator(color: Colors.greenAccent),
                      const SizedBox(height: 12),
                      const Text(
                        'Initializing Camera Access...',
                        style: TextStyle(color: Color(0xFFBBC9CD)),
                      ),
                      const SizedBox(height: 12),
                      TextButton.icon(
                        onPressed: _initializeCamera,
                        icon: const Icon(Icons.refresh, color: Colors.cyanAccent, size: 18),
                        label: const Text('Click to Start Camera', style: TextStyle(color: Colors.cyanAccent)),
                      ),
                    ],
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildWorkspacePanel() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      width: double.infinity,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPredictionSection(),
          const Divider(height: 24, color: Colors.white12),
          _buildSpeechSection(),
          const SizedBox(height: 10),
          _buildAvatarSection(),
          const SizedBox(height: 10),
          _buildPlaybackActions(),
        ],
      ),
    );
  }

  Widget _buildPredictionSection() {
    final canAppendPrediction = _currentPredictedLetter.isNotEmpty &&
        _currentPredictedLetter.toLowerCase() != 'none';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'MEDI-SIGN AI REAL-TIME INFERENCE:',
          style: TextStyle(
            color: Colors.grey,
            fontSize: 11,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                _predictionText,
                style: const TextStyle(
                  color: Colors.greenAccent,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            if (canAppendPrediction)
              ElevatedButton.icon(
                onPressed: _appendDetectedLetter,
                icon: const Icon(Icons.add, size: 14),
                label: const Text('Append'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.greenAccent[700],
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  textStyle: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            OutlinedButton.icon(
              onPressed: _appendSpace,
              icon: const Icon(Icons.space_bar, size: 14, color: Colors.white70),
              label: const Text(
                'Space',
                style: TextStyle(color: Colors.white70),
              ),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.white24),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              ),
            ),
            const SizedBox(width: 8),
            OutlinedButton.icon(
              onPressed: _removeLastCharacter,
              icon: const Icon(
                Icons.backspace_outlined,
                size: 14,
                color: Colors.redAccent,
              ),
              label: const Text(
                'Backspace',
                style: TextStyle(color: Colors.redAccent),
              ),
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Colors.redAccent.withOpacity(0.4)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSpeechSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'THE VERBALIZER (SPEECH SYNTHESIS):',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 11,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
            IconButton(
              icon: const Icon(Icons.refresh, size: 16, color: Colors.white54),
              onPressed: _loadVoices,
              tooltip: 'Reload Voices',
              constraints: const BoxConstraints(),
              padding: EdgeInsets.zero,
            ),
          ],
        ),
        const SizedBox(height: 8),
        _buildVoiceSelector(),
        const SizedBox(height: 10),
        if (_isRecording) _buildRecordingBanner(),
        _buildSentenceEditor(),
      ],
    );
  }

  Widget _buildVoiceSelector() {
    if (_isLoadingVoices) {
      return const LinearProgressIndicator(color: Colors.greenAccent);
    }

    if (_voices.isEmpty) {
      return const Text(
        'No voices available. Ensure TTS backend is running on port 5001.',
        style: TextStyle(color: Colors.amber, fontSize: 12),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF374151),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white10),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _selectedVoiceName,
          dropdownColor: const Color(0xFF1F2937),
          icon: const Icon(Icons.arrow_drop_down, color: Colors.greenAccent),
          isExpanded: true,
          style: const TextStyle(color: Colors.white, fontSize: 13),
          onChanged: (newValue) {
            setState(() {
              _selectedVoiceName = newValue;
            });
          },
          items: _voices.map((voice) {
            return DropdownMenuItem<String>(
              value: voice.name,
              child: Text(
                '${voice.shortName} (${voice.genderSymbol} | ${voice.locale})',
                overflow: TextOverflow.ellipsis,
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildRecordingBanner() {
    return const Padding(
      padding: EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Icon(
            Icons.fiber_manual_record,
            color: Colors.redAccent,
            size: 12,
          ),
          SizedBox(width: 6),
          Expanded(
            child: Text(
              'Recording clinician speech... Click mic again to stop and translate.',
              style: TextStyle(
                color: Colors.redAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSentenceEditor() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(
          child: TextField(
            controller: _sentenceController,
            maxLines: 2,
            decoration: InputDecoration(
              hintText: 'Assemble sign letters or type message here...',
              hintStyle: const TextStyle(color: Colors.grey, fontSize: 13),
              filled: true,
              fillColor: const Color(0xFF374151),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Colors.greenAccent),
              ),
              contentPadding: const EdgeInsets.all(12),
            ),
            style: const TextStyle(color: Colors.white, fontSize: 14),
          ),
        ),
        const SizedBox(width: 8),
        _isTranscribing ? _buildTranscribingIndicator() : _buildRecordingButton(),
      ],
    );
  }

  Widget _buildTranscribingIndicator() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blueAccent.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blueAccent.withOpacity(0.5)),
      ),
      child: const SizedBox(
        width: 24,
        height: 24,
        child: CircularProgressIndicator(
          strokeWidth: 2.5,
          color: Colors.blueAccent,
        ),
      ),
    );
  }

  Widget _buildRecordingButton() {
    return Container(
      decoration: BoxDecoration(
        color: _isRecording
            ? Colors.redAccent.withOpacity(0.2)
            : Colors.greenAccent.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: _isRecording
              ? Colors.redAccent
              : Colors.greenAccent.withOpacity(0.5),
          width: 1.5,
        ),
      ),
      child: IconButton(
        icon: Icon(
          _isRecording ? Icons.mic : Icons.mic_none,
          color: _isRecording ? Colors.redAccent : Colors.greenAccent,
        ),
        onPressed: _toggleRecording,
        tooltip: _isRecording
            ? 'Stop Recording & Transcribe'
            : 'Record Speech (Clinician Bridge)',
        style: IconButton.styleFrom(
          padding: const EdgeInsets.all(12),
        ),
      ),
    );
  }

  Widget _buildAvatarSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'TEXT TO SIGN AVATAR:',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildStatusChip(
                label: 'Tokens: ${_activeAvatarTokens.length}',
                backgroundColor: Colors.cyanAccent.withOpacity(0.08),
                borderColor: Colors.cyanAccent.withOpacity(0.25),
                textColor: Colors.cyanAccent,
              ),
              _buildStatusChip(
                label: _currentAvatarToken.isEmpty
                    ? 'Frame: Idle'
                    : 'Frame: $_currentAvatarToken',
                backgroundColor: Colors.greenAccent.withOpacity(0.08),
                borderColor: Colors.greenAccent.withOpacity(0.2),
                textColor: Colors.greenAccent,
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isParsingAvatarText || _isLoadingAvatarLibrary
                  ? null
                  : _parseAvatarTextAndPlay,
              icon: _isParsingAvatarText
                  ? const SizedBox(
                      width: 14,
                      height: 14,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.sign_language_outlined, size: 18),
              label: Text(
                _isParsingAvatarText
                    ? 'Parsing text...'
                    : _isPlayingAvatar
                        ? 'Replay Sign Animation'
                        : 'Convert Text to Sign',
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.cyan[700],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            height: 220,
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.cyanAccent.withOpacity(0.15)),
            ),
            child: _isLoadingAvatarLibrary
                ? const Center(
                    child: CircularProgressIndicator(color: Colors.cyanAccent),
                  )
                : CustomPaint(
                    painter: AvatarPosePainter(joints: _currentAvatarJoints),
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24),
                        child: Text(
                          _buildAvatarHintText(),
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.7),
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChip({
    required String label,
    required Color backgroundColor,
    required Color borderColor,
    required Color textColor,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: borderColor),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: textColor,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  String _buildAvatarHintText() {
    if (_currentAvatarJoints.isNotEmpty) {
      return 'Active token: $_currentAvatarToken';
    }

    if (_isPlayingAvatar) {
      return 'Transitioning between sign poses...';
    }

    return 'Use the sentence box above, then tap Convert Text to Sign.';
  }

  Widget _buildPlaybackActions() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _isSpeaking ? null : _speakText,
            icon: _isSpeaking
                ? const SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Icon(Icons.volume_up, size: 18),
            label: Text(_isSpeaking ? 'Speaking...' : 'PLAY SPEECH'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.greenAccent[700],
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        IconButton(
          icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
          onPressed: _clearSentence,
          tooltip: 'Clear Text',
          style: IconButton.styleFrom(
            backgroundColor: Colors.redAccent.withOpacity(0.1),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.all(12),
          ),
        ),
      ],
    );
  }
}
