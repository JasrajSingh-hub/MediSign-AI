import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:typed_data';
import 'package:record/record.dart';
import 'package:http_parser/http_parser.dart';
import 'package:file_picker/file_picker.dart';

// Global list of available device cameras
List<CameraDescription> cameras = [];

Future<void> main() async {
  // Ensure Flutter engine integrations are loaded before waking hardware up
  WidgetsFlutterBinding.ensureInitialized();

  try {
    cameras = await availableCameras();
  } catch (e) {
    print("Error finding cameras: $e");
  }

  runApp(const MediSignSandbox());
}

class MediSignSandbox extends StatelessWidget {
  const MediSignSandbox({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF111827),
      ),
      home: const TestDashboard(),
    );
  }
}

class TestDashboard extends StatelessWidget {
  const TestDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return const TestDashboardView();
  }
}

class TestDashboardView extends StatefulWidget {
  const TestDashboardView({super.key});

  @override
  State<TestDashboardView> createState() => _TestDashboardViewState();
}

class _TestDashboardViewState extends State<TestDashboardView> {
  CameraController? _controller;
  bool _isCameraInitialized = false;

  String _aiPredictionText = "Waiting for clinician sign language input...";
  String _currentPredictedLetter = "";
  Timer? _frameProcessingTimer;
  bool _isProcessingFrame = false;

  // Feature 2 (The Verbalizer) State variables
  final AudioPlayer _audioPlayer = AudioPlayer();
  final TextEditingController _sentenceController = TextEditingController();
  List<Map<String, dynamic>> _voices = [];
  String? _selectedVoice;
  bool _isLoadingVoices = false;
  bool _isSpeaking = false;

  // Feature 3 (The Transcriber / STT) State variables
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  bool _isTranscribing = false;

  // Prescription OCR Tab State variables
  int _currentTab = 0;
  PlatformFile? _pickedFile;
  bool _isProcessingOCR = false;
  Map<String, dynamic>? _ocrResult;
  String _ocrError = "";

  @override
  void initState() {
    super.initState();
    _initializeLocalCamera();
    _fetchVoices();
  }

  // Fetch available voices from the TTS backend service
  Future<void> _fetchVoices() async {
    if (mounted) {
      setState(() {
        _isLoadingVoices = true;
      });
    }
    try {
      final response = await http.get(
        Uri.parse('http://127.0.0.1:5000/api/v1/tts/voices'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> voiceList = data['voices'];
        if (mounted) {
          setState(() {
            _voices = voiceList
                .map((v) => Map<String, dynamic>.from(v))
                .toList();
            if (_voices.isNotEmpty) {
              // Select first en-IN or en-US voice as default, or fallback to first voice
              _selectedVoice = _voices.firstWhere(
                (v) =>
                    v['locale'].toString().toLowerCase().contains('in') ||
                    v['locale'].toString().toLowerCase().contains('us'),
                orElse: () => _voices.first,
              )['name'];
            }
          });
        }
      }
    } catch (e) {
      print("Failed to fetch voices from TTS service: $e");
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingVoices = false;
        });
      }
    }
  }

  // Synthesize text and play audio directly from memory bytes
  Future<void> _speakText(String text) async {
    if (text.trim().isEmpty) return;
    if (mounted) {
      setState(() {
        _isSpeaking = true;
      });
    }

    try {
      String language = "en-US";
      if (_selectedVoice != null) {
        final voice = _voices.firstWhere(
          (v) => v['name'] == _selectedVoice,
          orElse: () => {},
        );
        if (voice.containsKey('locale')) {
          language = voice['locale'];
        }
      }

      final response = await http.post(
        Uri.parse('http://127.0.0.1:5000/api/v1/tts/speak'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'text': text,
          'language': language,
          'session_id':
              'flutter-session-${DateTime.now().millisecondsSinceEpoch}',
        }),
      );

      if (response.statusCode == 200) {
        // Play the synthesized audio stream bytes directly in memory
        await _audioPlayer.play(BytesSource(response.bodyBytes));
      } else {
        final err = jsonDecode(response.body);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                "TTS Error: ${err['detail'] ?? 'Failed to synthesize speech'}",
              ),
            ),
          );
        }
      }
    } catch (e) {
      print("Error calling TTS speak API: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Error: Cannot connect to TTS backend service"),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSpeaking = false;
        });
      }
    }
  }

  // Universally safe camera configuration routine
  void _initializeLocalCamera() async {
    if (cameras.isEmpty) {
      try {
        cameras = await availableCameras();
      } catch (e) {
        print("Camera lookup failed: $e");
      }
    }

    if (cameras.isEmpty) return;

    _controller = CameraController(
      cameras[0],
      ResolutionPreset
          .low, // Kept small so matrix payload travels fast down the USB wire
      enableAudio: false,
    );

    try {
      await _controller!.initialize();
      if (!mounted) return;

      setState(() {
        _isCameraInitialized = true;
      });

      // Bypasses the Mali GPU format bug using a safe file capture interval clock loop
      _frameProcessingTimer = Timer.periodic(
        const Duration(milliseconds: 300),
        (timer) async {
          if (_isProcessingFrame ||
              _controller == null ||
              !_controller!.value.isInitialized ||
              _controller!.value.isTakingPicture) {
            return;
          }

          if (mounted) {
            setState(() {
              _isProcessingFrame = true;
            });
          }

          await _captureAndSendFrameUniversal();

          if (mounted) {
            setState(() {
              _isProcessingFrame = false;
            });
          }
        },
      );
    } catch (e) {
      print("Camera hardware configuration error: $e");
    }
  }

  // Standard format capture bridge pipeline
  Future<void> _captureAndSendFrameUniversal() async {
    try {
      // 1. Snaps a perfectly standard photo file structure
      XFile pictureFile = await _controller!.takePicture();
      File file = File(pictureFile.path);

      // 2. Read file binary structure directly into memory array
      List<int> imageBytes = await file.readAsBytes();
      String base64Image = base64Encode(imageBytes);

      // 3. Prevent data storage bloating by immediately cleaning up the temporary file
      await file.delete();

      // 4. Fire the payload through the locked USB ADB mapping tunnel
      var url = Uri.parse('http://127.0.0.1:5000/predict');

      var response = await http
          .post(
            url,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({"image": "data:image/jpeg;base64,$base64Image"}),
          )
          .timeout(const Duration(milliseconds: 400));

      if (response.statusCode == 200 && mounted) {
        var data = jsonDecode(response.body);
        setState(() {
          String rawLetter = data['letter'] ?? "";
          _aiPredictionText =
              "Detected Sign: $rawLetter (${data['confidence']})";
          _currentPredictedLetter = rawLetter;
        });
      }
    } catch (e) {
      // Quietly drop connection lag spikes to prevent execution logs bloating
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
      if (await _audioRecorder.hasPermission()) {
        const config = RecordConfig(
          encoder: AudioEncoder.pcm16bits,
          sampleRate: 16000,
          numChannels: 1,
        );

        await _audioRecorder.start(config, path: '');
        setState(() {
          _isRecording = true;
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Microphone permission denied")),
        );
      }
    } catch (e) {
      print("Error starting recording: $e");
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Failed to start recording: $e")));
    }
  }

  Future<void> _stopRecordingAndTranscribe() async {
    try {
      setState(() {
        _isRecording = false;
        _isTranscribing = true;
      });

      final path = await _audioRecorder.stop();
      if (path == null || path.isEmpty) {
        throw Exception("No audio recorded");
      }

      Uint8List audioBytes;
      if (kIsWeb) {
        final response = await http.get(Uri.parse(path));
        audioBytes = response.bodyBytes;
      } else {
        audioBytes = await File(path).readAsBytes();
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('http://127.0.0.1:5000/api/v1/stt/transcribe'),
      );

      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          audioBytes,
          filename: 'audio.wav',
          contentType: MediaType('audio', 'wav'),
        ),
      );

      String language = "en-US";
      if (_selectedVoice != null) {
        final voice = _voices.firstWhere(
          (v) => v['name'] == _selectedVoice,
          orElse: () => {},
        );
        if (voice.containsKey('locale')) {
          language = voice['locale'];
        }
      }
      request.fields['language'] = language;

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final transcribedText = data['text'] ?? "";
        setState(() {
          if (_sentenceController.text.isEmpty) {
            _sentenceController.text = transcribedText;
          } else {
            _sentenceController.text += " $transcribedText";
          }
        });
      } else {
        final err = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              "STT Error: ${err['detail'] ?? 'Failed to transcribe speech'}",
            ),
          ),
        );
      }
    } catch (e) {
      print("Error stopping recording or transcribing: $e");
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Transcription failed: $e")));
    } finally {
      setState(() {
        _isTranscribing = false;
      });
    }
  }

  Widget _buildMicButton() {
    if (_isTranscribing) {
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
            ? "Stop Recording & Transcribe"
            : "Record Speech (Clinician Bridge)",
        style: IconButton.styleFrom(padding: const EdgeInsets.all(12)),
      ),
    );
  }

  Future<void> _pickPrescriptionFile() async {
    try {
      FilePickerResult? result = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['jpg', 'jpeg', 'png'],
      );

      if (result != null) {
        setState(() {
          _pickedFile = result.files.first;
          _ocrResult = null;
          _ocrError = "";
        });
      }
    } catch (e) {
      setState(() {
        _ocrError = "Failed to select image: $e";
      });
    }
  }

  Future<void> _processOCR() async {
    if (_pickedFile == null) return;
    setState(() {
      _isProcessingOCR = true;
      _ocrError = "";
    });

    try {
      var uri = Uri.parse('http://127.0.0.1:5000/api/v1/prescription/process');
      var request = http.MultipartRequest('POST', uri);
      request.fields['uploaded_by'] = 'Flutter Clinician UI';

      if (kIsWeb) {
        if (_pickedFile!.bytes != null) {
          request.files.add(
            http.MultipartFile.fromBytes(
              'file',
              _pickedFile!.bytes!,
              filename: _pickedFile!.name,
              contentType: MediaType('image', _pickedFile!.extension ?? 'png'),
            ),
          );
        } else {
          throw Exception("File contents empty.");
        }
      } else {
        if (_pickedFile!.path != null) {
          request.files.add(
            await http.MultipartFile.fromPath(
              'file',
              _pickedFile!.path!,
              contentType: MediaType('image', _pickedFile!.extension ?? 'png'),
            ),
          );
        } else {
          throw Exception("File path unavailable.");
        }
      }

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        setState(() {
          _ocrResult = jsonDecode(response.body);
        });
      } else {
        final err = jsonDecode(response.body);
        setState(() {
          _ocrError = err['detail'] ?? "Server returned error: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _ocrError = "OCR request failed: $e";
      });
    } finally {
      setState(() {
        _isProcessingOCR = false;
      });
    }
  }

  @override
  void dispose() {
    // Clear the active timer loop and release camera hooks on exit
    _frameProcessingTimer?.cancel();
    _controller?.dispose();
    _sentenceController.dispose();
    _audioPlayer.dispose();
    _audioRecorder.dispose();
    super.dispose();
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: _currentTab == 0 ? _buildTranslatorTab() : _buildOCRTab(),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTab,
        onTap: (index) {
          setState(() {
            _currentTab = index;
          });
        },
        selectedItemColor: Colors.greenAccent,
        unselectedItemColor: Colors.grey,
        backgroundColor: const Color(0xFF1F2937),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.translate),
            label: "Sign Language",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt_long),
            label: "Prescription OCR",
          ),
        ],
      ),
    );
  }

  Widget _buildTranslatorTab() {
    return Column(
      children: [
        // 1. TOP HALF: Vision Workspace Mirror Frame
        Expanded(
          flex: 4,
          child: Container(
            margin: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF1F2937),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white10),
            ),
            width: double.infinity,
            child: _isCameraInitialized && _controller != null
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: CameraPreview(_controller!),
                  )
                : const Center(
                    child: CircularProgressIndicator(
                      color: Colors.greenAccent,
                    ),
                  ),
          ),
        ),

        // 2. BOTTOM HALF: Interactive Translation Builder & Verbalizer
        Expanded(
          flex: 5,
          child: SingleChildScrollView(
            child: Container(
              margin: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 4,
              ),
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
                  // Prediction Header
                  const Text(
                    "MEDI-SIGN AI REAL-TIME INFERENCE:",
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Prediction Text & Append Button
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          _aiPredictionText,
                          style: const TextStyle(
                            color: Colors.greenAccent,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      if (_currentPredictedLetter.isNotEmpty &&
                          _currentPredictedLetter.toLowerCase() != 'none')
                        ElevatedButton.icon(
                          onPressed: () {
                            String toAdd = _currentPredictedLetter;
                            setState(() {
                              _sentenceController.text += toAdd;
                            });
                          },
                          icon: const Icon(Icons.add, size: 14),
                          label: const Text("Append"),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.greenAccent[700],
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
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

                  // Text tools: Space & Backspace
                  Row(
                    children: [
                      OutlinedButton.icon(
                        onPressed: () {
                          setState(() {
                            _sentenceController.text += " ";
                          });
                        },
                        icon: const Icon(
                          Icons.space_bar,
                          size: 14,
                          color: Colors.white70,
                        ),
                        label: const Text(
                          "Space",
                          style: TextStyle(color: Colors.white70),
                        ),
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: Colors.white24),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(6),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 6,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () {
                          String current = _sentenceController.text;
                          if (current.isNotEmpty) {
                            setState(() {
                              _sentenceController.text = current.substring(
                                0,
                                current.length - 1,
                              );
                            });
                          }
                        },
                        icon: const Icon(
                          Icons.backspace_outlined,
                          size: 14,
                          color: Colors.redAccent,
                        ),
                        label: const Text(
                          "Backspace",
                          style: TextStyle(color: Colors.redAccent),
                        ),
                        style: OutlinedButton.styleFrom(
                          side: BorderSide(
                            color: Colors.redAccent.withOpacity(0.4),
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(6),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 6,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const Divider(height: 24, color: Colors.white12),

                  // TTS Section Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        "THE VERBALIZER (SPEECH SYNTHESIS):",
                        style: TextStyle(
                          color: Colors.grey,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(
                          Icons.refresh,
                          size: 16,
                          color: Colors.white54,
                        ),
                        onPressed: _fetchVoices,
                        tooltip: "Reload Voices",
                        constraints: const BoxConstraints(),
                        padding: EdgeInsets.zero,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Dropdown Voice list
                  if (_isLoadingVoices)
                    const LinearProgressIndicator(color: Colors.greenAccent)
                  else if (_voices.isEmpty)
                    const Text(
                      "No voices available. Ensure TTS backend is running on port 5000.",
                      style: TextStyle(color: Colors.amber, fontSize: 12),
                    )
                  else
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFF374151),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedVoice,
                          dropdownColor: const Color(0xFF1F2937),
                          icon: const Icon(
                            Icons.arrow_drop_down,
                            color: Colors.greenAccent,
                          ),
                          isExpanded: true,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                          ),
                          onChanged: (String? newValue) {
                            setState(() {
                              _selectedVoice = newValue;
                            });
                          },
                          items: _voices.map<DropdownMenuItem<String>>((
                            Map<String, dynamic> voice,
                          ) {
                            String genderIcon =
                                voice['gender'].toString().toLowerCase() ==
                                        'female'
                                    ? '♀'
                                    : '♂';
                            String displayName = voice['name']
                                .toString()
                                .split('-')
                                .last;
                            return DropdownMenuItem<String>(
                              value: voice['name'],
                              child: Text(
                                "$displayName ($genderIcon | ${voice['locale']})",
                                overflow: TextOverflow.ellipsis,
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                  const SizedBox(height: 10),

                  // Edit Phrase Field
                  if (_isRecording)
                    const Padding(
                      padding: EdgeInsets.only(bottom: 6.0),
                      child: Row(
                        children: [
                          Icon(
                            Icons.fiber_manual_record,
                            color: Colors.redAccent,
                            size: 12,
                          ),
                          SizedBox(width: 6),
                          Text(
                            "Recording clinician speech... Click mic again to stop and translate.",
                            style: TextStyle(
                              color: Colors.redAccent,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _sentenceController,
                          maxLines: 2,
                          decoration: InputDecoration(
                            hintText:
                                "Assemble sign letters or type message here...",
                            hintStyle: const TextStyle(
                              color: Colors.grey,
                              fontSize: 13,
                            ),
                            filled: true,
                            fillColor: const Color(0xFF374151),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: BorderSide.none,
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: const BorderSide(
                                color: Colors.greenAccent,
                              ),
                            ),
                            contentPadding: const EdgeInsets.all(12),
                          ),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      _buildMicButton(),
                    ],
                  ),
                  const SizedBox(height: 10),

                  // PLAY SPEECH & CLEAR
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isSpeaking
                              ? null
                              : () => _speakText(_sentenceController.text),
                          icon: _isSpeaking
                              ? const SizedBox(
                                  width: 14,
                                  height: 14,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2.0,
                                    color: Colors.white,
                                  ),
                                )
                              : const Icon(Icons.volume_up, size: 18),
                          label: Text(
                            _isSpeaking ? "Speaking..." : "PLAY SPEECH",
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.greenAccent[700],
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                              vertical: 12,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(
                          Icons.delete_outline,
                          color: Colors.redAccent,
                        ),
                        onPressed: () {
                          setState(() {
                            _sentenceController.clear();
                          });
                        },
                        tooltip: "Clear Text",
                        style: IconButton.styleFrom(
                          backgroundColor: Colors.redAccent.withOpacity(
                            0.1,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          padding: const EdgeInsets.all(12),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildOCRTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1E3A8A), Color(0xFF0F766E)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.receipt_long, size: 36, color: Colors.greenAccent),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text(
                        "Prescription OCR Scanner",
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        "Upload a prescription image to extract structured patient parameters and run drug safety validations.",
                        style: TextStyle(fontSize: 11, color: Colors.white70),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // File Picker Block
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1F2937),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white10),
            ),
            child: Column(
              children: [
                if (_pickedFile == null)
                  Column(
                    children: [
                      const Icon(Icons.cloud_upload_outlined, size: 54, color: Colors.grey),
                      const SizedBox(height: 10),
                      const Text(
                        "No prescription file selected",
                        style: TextStyle(color: Colors.grey, fontSize: 13),
                      ),
                      const SizedBox(height: 14),
                      ElevatedButton.icon(
                        onPressed: _pickPrescriptionFile,
                        icon: const Icon(Icons.image_search, size: 18),
                        label: const Text("Select Prescription Image"),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.greenAccent[700],
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  )
                else
                  Column(
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.insert_drive_file, color: Colors.greenAccent, size: 32),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _pickedFile!.name,
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                                  overflow: TextOverflow.ellipsis,
                                ),
                                Text(
                                  "${(_pickedFile!.size / 1024).toStringAsFixed(1)} KB",
                                  style: const TextStyle(color: Colors.grey, fontSize: 11),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.cancel, color: Colors.redAccent, size: 20),
                            onPressed: () {
                              setState(() {
                                _pickedFile = null;
                                _ocrResult = null;
                                _ocrError = "";
                              });
                            },
                          )
                        ],
                      ),
                      if (kIsWeb && _pickedFile!.bytes != null) ...[
                        const SizedBox(height: 16),
                        Container(
                          height: 150,
                          width: double.infinity,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.white10),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.memory(_pickedFile!.bytes!, fit: BoxFit.contain),
                          ),
                        ),
                      ],
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _isProcessingOCR ? null : _processOCR,
                              icon: _isProcessingOCR
                                  ? const SizedBox(
                                      width: 14,
                                      height: 14,
                                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                    )
                                  : const Icon(Icons.analytics, size: 18),
                              label: Text(_isProcessingOCR ? "Processing OCR..." : "Analyze Prescription"),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blueAccent[700],
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                if (_ocrError.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    _ocrError,
                    style: const TextStyle(color: Colors.redAccent, fontSize: 12),
                    textAlign: TextAlign.center,
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Output View
          if (_ocrResult != null) _buildOCRResultView(),
        ],
      ),
    );
  }

  Widget _buildOCRResultView() {
    final data = _ocrResult!['structured_data'] ?? {};
    final medicines = data['medicines'] as List<dynamic>? ?? [];
    final warnings = _ocrResult!['warnings'] as List<dynamic>? ?? [];
    final double confidence = (_ocrResult!['confidence'] as num? ?? 0.0) * 100;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              "PRESCRIPTION DETAILS:",
              style: TextStyle(
                color: Colors.grey,
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: confidence > 70 ? Colors.green[900]!.withOpacity(0.4) : Colors.amber[900]!.withOpacity(0.4),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: confidence > 70 ? Colors.green : Colors.amber),
              ),
              child: Text(
                "OCR Score: ${confidence.toStringAsFixed(1)}%",
                style: TextStyle(
                  color: confidence > 70 ? Colors.greenAccent : Colors.amberAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                ),
              ),
            )
          ],
        ),
        const SizedBox(height: 10),

        // Metadata Card
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF1F2937),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white10),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildMetaRow(Icons.local_hospital, "Hospital:", data['hospital_name'] ?? "Not Detected"),
              _buildMetaRow(Icons.person_pin, "Doctor:", data['doctor_name'] ?? "Not Detected"),
              const Divider(color: Colors.white12, height: 12),
              _buildMetaRow(Icons.person, "Patient Name:", data['patient_name'] ?? "Not Detected"),
              Row(
                children: [
                  Expanded(child: _buildMetaRow(Icons.cake, "Age:", data['age'] ?? "Not Detected")),
                  Expanded(child: _buildMetaRow(Icons.wc, "Sex:", data['gender'] ?? "Not Detected")),
                ],
              ),
              _buildMetaRow(Icons.calendar_today, "Date:", data['date'] ?? "Not Detected"),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Medication Safety Audit
        const Text(
          "SAFETY VERIFICATION AUDIT:",
          style: TextStyle(
            color: Colors.grey,
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: warnings.isNotEmpty ? Colors.redAccent.withOpacity(0.1) : Colors.greenAccent.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: warnings.isNotEmpty ? Colors.redAccent.withOpacity(0.3) : Colors.greenAccent.withOpacity(0.3)),
          ),
          child: warnings.isNotEmpty
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Icon(Icons.warning_amber_rounded, color: Colors.redAccent, size: 18),
                        SizedBox(width: 6),
                        Text(
                          "Safety Warning Alert!",
                          style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    ...warnings.map((w) => Padding(
                          padding: const EdgeInsets.only(bottom: 4.0),
                          child: Text("• $w", style: const TextStyle(color: Colors.white70, fontSize: 12)),
                        )),
                  ],
                )
              : Row(
                  children: const [
                    Icon(Icons.check_circle_outline, color: Colors.greenAccent, size: 18),
                    SizedBox(width: 6),
                    Text(
                      "No safety warning flags found. Prescription safe.",
                      style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                  ],
                ),
        ),
        const SizedBox(height: 16),

        // Medicines cards
        const Text(
          "PRESCRIBED MEDICINES:",
          style: TextStyle(
            color: Colors.grey,
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 8),
        if (medicines.isEmpty)
          const Text("No medicines extracted.", style: TextStyle(color: Colors.grey, fontSize: 12))
        else
          ...medicines.map((med) => Card(
                color: const Color(0xFF374151),
                margin: const EdgeInsets.only(bottom: 8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        med['name'] ?? "Unknown Medicine",
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.greenAccent),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Expanded(child: _buildMedDetail("Dose", med['dose'])),
                          Expanded(child: _buildMedDetail("Frequency", med['frequency'])),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Expanded(child: _buildMedDetail("Duration", med['duration'])),
                          Expanded(child: _buildMedDetail("Instructions", med['instructions'])),
                        ],
                      ),
                    ],
                  ),
                ),
              )),
        const SizedBox(height: 16),

        // Expandable raw text
        Theme(
          data: ThemeData.dark().copyWith(dividerColor: Colors.transparent),
          child: ExpansionTile(
            title: const Text(
              "RAW EXTRACTED TEXT (DEBUG)",
              style: TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.2),
            ),
            tilePadding: EdgeInsets.zero,
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.black38,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.white10),
                ),
                child: Text(
                  _ocrResult!['raw_text'] ?? "Empty",
                  style: const TextStyle(fontFamily: 'Courier', fontSize: 11, color: Colors.white70),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMetaRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Row(
        children: [
          Icon(icon, size: 14, color: Colors.grey),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          const SizedBox(width: 4),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMedDetail(String label, String? value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 1),
        Text(
          (value == null || value.trim().isEmpty) ? "-" : value,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
        ),
      ],
    );
  }
}
