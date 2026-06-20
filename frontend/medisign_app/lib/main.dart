import 'package:flutter/material.dart';
import 'package:camera/camera.dart'; 
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'dart:io';

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

class TestDashboard extends StatefulWidget {
  const TestDashboard({super.key});

  @override
  State<TestDashboard> createState() => _TestDashboardState();
}

class _TestDashboardState extends State<TestDashboard> {
  CameraController? _controller;
  bool _isCameraInitialized = false;

  String _aiPredictionText = "Waiting for clinician sign language input...";
  Timer? _frameProcessingTimer;
  bool _isProcessingFrame = false;

  @override
  void initState() {
    super.initState();
    _initializeLocalCamera();
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
      ResolutionPreset.low, // Kept small so matrix payload travels fast down the USB wire
      enableAudio: false,
    );

    try {
      await _controller!.initialize();
      if (!mounted) return;

      setState(() {
        _isCameraInitialized = true;
      });

      // Bypasses the Mali GPU format bug using a safe file capture interval clock loop
      _frameProcessingTimer = Timer.periodic(const Duration(milliseconds: 300), (timer) async {
        if (_isProcessingFrame || _controller == null || !_controller!.value.isInitialized || _controller!.value.isTakingPicture) {
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
      });

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

      var response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"image": "data:image/jpeg;base64,$base64Image"}),
      ).timeout(const Duration(milliseconds: 400));

      if (response.statusCode == 200 && mounted) {
        var data = jsonDecode(response.body);
        setState(() {
          _aiPredictionText = "Detected Sign: ${data['letter']} (${data['confidence']})";
        });
      }
    } catch (e) {
      // Quietly drop connection lag spikes to prevent execution logs bloating
    }
  }

  @override
  void dispose() {
    // Clear the active timer loop and release camera hooks on exit
    _frameProcessingTimer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // 1. TOP HALF: Vision Workspace Mirror Frame
            Expanded(
              child: Container(
                margin: const EdgeInsets.all(12),
                color: const Color(0xFF1F2937),
                width: double.infinity,
                child: _isCameraInitialized && _controller != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: CameraPreview(_controller!),
                      )
                    : const Center(
                        child: CircularProgressIndicator(
                          color: Colors.greenAccent,
                        ),
                      ),
              ),
            ),

            // 2. BOTTOM HALF: Dynamic Translation Component Text Panel
            Expanded(
              child: Container(
                margin: const EdgeInsets.all(12),
                padding: const EdgeInsets.all(16),
                color: const Color.fromRGBO(31, 41, 55, 1),
                width: double.infinity,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "MEDI-SIGN AI TRANSLATION OUTPUT:",
                      style: TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 20),
                    Text(
                      _aiPredictionText,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}