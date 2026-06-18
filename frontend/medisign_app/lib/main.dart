import 'package:flutter/material.dart';
import 'package:camera/camera.dart'; // Import the new camera package
import 'package:http/http.dart' as http; 
import 'dart:convert';
import 'dart:async';
import 'dart:io';
// We need to store a global list of available cameras on the laptop
List<CameraDescription> cameras = [];

Future<void> main() async {
  // Ensure Flutter engine integrations are loaded before waking hardware up
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // Look at your laptop motherboard connections and find all webcams
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

// We change this to a StatefulWidget because the camera status changes over time
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

  @override
  void initState() {
    super.initState();
    _initializeLocalCamera();
  }   

  Future<void> _initializeLocalCamera() async {
    if (cameras.isEmpty) return;

    // Select the first camera found (index 0 is your default built-in webcam)
    _controller = CameraController(
      cameras[0],
      ResolutionPreset
          .medium, // Don't use max resolution to save processing RAM
    );

    try {
      // Boot up the hardware sensor camera pipe
      await _controller!.initialize();
      if (!mounted) return;

      setState(() {
        _isCameraInitialized = true; // Tell the UI it's safe to show video!
      });
    } catch (e) {
      print("Camera initialization failed: $e");
    }
  }


Future<void> _captureAndSendFrame() async {
    if (!_isCameraInitialized || _controller == null || _controller!.value.isTakingPicture) {
      return;
    }

    try {
      // Take a silent temporary snapshot snapshot
      XFile pictureFile = await _controller!.takePicture();
      File file = File(pictureFile.path);
      
      // Read bytes and convert to base64 text string
      List<int> imageBytes = await file.readAsBytes();
      String base64Image = base64Encode(imageBytes);

      // Clean up the temporary cached file immediately to preserve device memory
      await file.delete();

      // IF TESTING ON EMULATOR: Use 10.0.2.2 to point to your computer's local ports
      // IF TESTING ON PHYSICAL DEVICE: Use your machine's exact local IP (e.g., 192.168.1.X)
      var url = Uri.parse('http://10.0.2.2:5000/predict');

      var response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"image": "data:image/jpeg;base64,$base64Image"}),
      );

      if (response.statusCode == 200 && mounted) {
        var data = jsonDecode(response.body);
        setState(() {
          // Update the live subtitle block text state
          _aiPredictionText = "Detected Sign: ${data['letter']} (${data['confidence']})";
        });
      }
    } catch (e) {
      print("Connection to Flask API failed: $e");
    }
  }

  @override
  void dispose() {
    // Clean up memory and turn the webcam hardware light off when exiting
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // 1. TOP HALF: Jasraj's Vision Workspace (Now with live feed!)
            Expanded(
              child: Container(
                margin: const EdgeInsets.all(12),
                color: const Color(0xFF1F2937),
                width: double.infinity,
                child: _isCameraInitialized
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: CameraPreview(
                          _controller!,
                        ), // Renders your webcam stream!
                      )
                    : const Center(
                        child: CircularProgressIndicator(
                          color: Colors.greenAccent,
                        ),
                      ),
              ),
            ),

            // 2. BOTTOM HALF: Jaskaran's Subtitle Box Panel
            Expanded(
              child: Container(
                margin: const EdgeInsets.all(12),
                padding: const EdgeInsets.all(16),
                color: const Color(0xFF1F2937),
                width: double.infinity,
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "JASKARAN'S COMPONENT SUBTITLES:",
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    SizedBox(height: 20),
                    Text(
                      "Waiting for clinician voice ingestion stream...",
                      style: TextStyle(
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
