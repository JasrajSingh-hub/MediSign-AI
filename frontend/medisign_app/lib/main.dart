import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:image/image.dart' as img_lib;
import 'package:shared_preferences/shared_preferences.dart';

import 'emergency_view.dart';

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
        colorScheme: const ColorScheme.dark(
          primary: Colors.greenAccent,
          secondary: Colors.redAccent,
          surface: Color(0xFF1F2937),
        ),
      ),
      home: const MainShell(),
    );
  }
}

// Shell managing the BottomNavigationBar routing
class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentTabIndex = 0;

  @override
  Widget build(BuildContext context) {
    final List<Widget> tabs = [
      const TestDashboard(), // Tab 1: Sign Language Translation
      EmergencyScreen(cameras: cameras), // Tab 2: Emergency Detection
      const SettingsScreen(), // Tab 3: Configuration & System Status
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentTabIndex,
        children: tabs,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTabIndex,
        selectedItemColor: _currentTabIndex == 1 ? Colors.redAccent : Colors.greenAccent,
        unselectedItemColor: Colors.grey,
        backgroundColor: const Color(0xFF1F2937),
        onTap: (index) {
          setState(() {
            _currentTabIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.translate),
            label: "Sign Language",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.warning_amber_rounded),
            label: "Emergency",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: "Settings",
          ),
        ],
      ),
    );
  }
}

// Background isolate image compression helper for Sign Language view
List<int> _compressSignImage(List<int> rawBytes) {
  try {
    final image = img_lib.decodeImage(Uint8List.fromList(rawBytes));
    if (image == null) return rawBytes;
    final resized = img_lib.copyResize(image, width: 256);
    return img_lib.encodeJpg(resized, quality: 70);
  } catch (_) {
    return rawBytes;
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
  
  String _signUrl = 'http://127.0.0.1:5000/predict';
  int _intervalMs = 300;

  @override
  void initState() {
    super.initState();
    _loadConfig().then((_) {
      _initializeLocalCamera();
    });
  }

  Future<void> _loadConfig() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _signUrl = prefs.getString('sign_url') ?? 'http://127.0.0.1:5000/predict';
      _intervalMs = prefs.getInt('frame_interval_ms') ?? 300;
    });
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
      ResolutionPreset.low,
      enableAudio: false,
    );

    try {
      await _controller!.initialize();
      if (!mounted) return;

      setState(() {
        _isCameraInitialized = true;
      });

      _frameProcessingTimer?.cancel();
      _frameProcessingTimer = Timer.periodic(Duration(milliseconds: _intervalMs), (timer) async {
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
      XFile pictureFile = await _controller!.takePicture();
      File file = File(pictureFile.path);
      
      List<int> imageBytes = await file.readAsBytes();
      await file.delete();

      // Background compression isolate
      final compressedBytes = await compute(_compressSignImage, imageBytes);
      String base64Image = base64Encode(compressedBytes);

      var url = Uri.parse(_signUrl);
      var response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"image": "data:image/jpeg;base64,$base64Image"}),
      ).timeout(const Duration(milliseconds: 1000));

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
    _frameProcessingTimer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Sign Language translation", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.greenAccent)),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // 1. TOP HALF: Vision Workspace Mirror Frame
            Expanded(
              child: Container(
                margin: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF1F2937),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF374151)),
                ),
                width: double.infinity,
                child: _isCameraInitialized && _controller != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(10),
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
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF1F2937),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF374151)),
                ),
                width: double.infinity,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "MEDI-SIGN AI TRANSLATION OUTPUT:",
                      style: TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      _aiPredictionText,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 22,
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

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _signUrlController = TextEditingController();
  final _emergencyUrlController = TextEditingController();
  
  double _threshold = 0.80;
  int _intervalMs = 300;
  bool _enableAlarm = true;
  bool _enableVibration = true;
  bool _enableTts = true;
  bool _mockMode = false;

  // Developer Mode toggles
  int _titleTapCount = 0;
  bool _devModeUnlocked = false;

  // Exposing model metadata
  Map<String, dynamic> _modelMetadata = {};
  bool _isLoadingMetadata = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _signUrlController.text = prefs.getString('sign_url') ?? 'http://127.0.0.1:5000/predict';
      _emergencyUrlController.text = prefs.getString('emergency_url') ?? 'http://127.0.0.1:8000';
      _threshold = prefs.getDouble('confidence_threshold') ?? 0.80;
      _intervalMs = prefs.getInt('frame_interval_ms') ?? 300;
      _enableAlarm = prefs.getBool('enable_alarm') ?? true;
      _enableVibration = prefs.getBool('enable_vibration') ?? true;
      _enableTts = prefs.getBool('enable_tts') ?? true;
      _mockMode = prefs.getBool('mock_mode') ?? false;
      _devModeUnlocked = prefs.getBool('dev_mode_unlocked') ?? false;
    });

    if (_devModeUnlocked) {
      _fetchModelMetadata();
    }
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('sign_url', _signUrlController.text);
    await prefs.setString('emergency_url', _emergencyUrlController.text);
    await prefs.setDouble('confidence_threshold', _threshold);
    await prefs.setInt('frame_interval_ms', _intervalMs);
    await prefs.setBool('enable_alarm', _enableAlarm);
    await prefs.setBool('enable_vibration', _enableVibration);
    await prefs.setBool('enable_tts', _enableTts);
    await prefs.setBool('mock_mode', _mockMode);
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Settings saved successfully!"),
          backgroundColor: Colors.greenAccent,
        ),
      );
    }
  }

  void _handleTitleTap() async {
    if (_devModeUnlocked) return;

    setState(() {
      _titleTapCount++;
    });

    if (_titleTapCount >= 7) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('dev_mode_unlocked', true);
      setState(() {
        _devModeUnlocked = true;
      });
      _fetchModelMetadata();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Developer Mode Unlocked! 🚀"),
            backgroundColor: Colors.purpleAccent,
          ),
        );
      }
    }
  }

  Future<void> _fetchModelMetadata() async {
    setState(() {
      _isLoadingMetadata = true;
    });

    try {
      final response = await http.get(Uri.parse('${_emergencyUrlController.text}/status')).timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _modelMetadata = data['details'] ?? data;
        });
      }
    } catch (_) {
      setState(() {
        _modelMetadata = {"error": "Failed to fetch model metadata. Check if server is running."};
      });
    } finally {
      setState(() {
        _isLoadingMetadata = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: GestureDetector(
          onTap: _handleTitleTap,
          child: const Text(
            "MediSign Settings & Diagnostics",
            style: TextStyle(fontWeight: FontWeight.bold, color: Colors.greenAccent),
          ),
        ),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // API Server Addresses
            const Text(
              "SERVER CONFIGURATIONS",
              style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _signUrlController,
              decoration: const InputDecoration(
                labelText: "Sign Language API Endpoint",
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Color(0xFF1F2937),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _emergencyUrlController,
              decoration: const InputDecoration(
                labelText: "Emergency API Gateway Endpoint",
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Color(0xFF1F2937),
              ),
            ),
            const SizedBox(height: 20),

            // Prediction settings
            const Text(
              "PREDICTION OPTIONS",
              style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            
            // Confidence Threshold Slider
            ListTile(
              title: const Text("Confidence Alert Threshold"),
              subtitle: Text("${(_threshold * 100).toStringAsFixed(0)}%"),
              trailing: SizedBox(
                width: 180,
                child: Slider(
                  value: _threshold,
                  min: 0.50,
                  max: 1.00,
                  divisions: 10,
                  activeColor: Colors.redAccent,
                  onChanged: (val) {
                    setState(() {
                      _threshold = val;
                    });
                  },
                ),
              ),
            ),

            // Frame Processing Speed Dropdown
            ListTile(
              title: const Text("Frame Loop Interval"),
              trailing: DropdownButton<int>(
                value: _intervalMs,
                dropdownColor: const Color(0xFF1F2937),
                items: const [
                  DropdownMenuItem(value: 300, child: Text("300 ms (Fast)")),
                  DropdownMenuItem(value: 400, child: Text("400 ms")),
                  DropdownMenuItem(value: 500, child: Text("500 ms (Balanced)")),
                ],
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      _intervalMs = val;
                    });
                  }
                },
              ),
            ),

            const SizedBox(height: 20),

            // Alarm Engine Triggers
            const Text(
              "EMERGENCY ALERT MECHANISMS",
              style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            SwitchListTile(
              title: const Text("Audio Alarm Sound"),
              value: _enableAlarm,
              activeColor: Colors.redAccent,
              onChanged: (val) {
                setState(() {
                  _enableAlarm = val;
                });
              },
            ),
            SwitchListTile(
              title: const Text("Haptic Device Vibration"),
              value: _enableVibration,
              activeColor: Colors.redAccent,
              onChanged: (val) {
                setState(() {
                  _enableVibration = val;
                });
              },
            ),
            SwitchListTile(
              title: const Text("TTS Announcement Speak"),
              value: _enableTts,
              activeColor: Colors.redAccent,
              onChanged: (val) {
                setState(() {
                  _enableTts = val;
                });
              },
            ),

            // Save settings button
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.greenAccent,
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: _saveSettings,
                child: const Text("Save & Apply Configurations", style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
            
            // Developer Mode diagnostics
            if (_devModeUnlocked) ...[
              const SizedBox(height: 30),
              const Divider(color: Color(0xFF374151)),
              const SizedBox(height: 10),
              const Text(
                "DEVELOPER & METADATA DIAGNOSTICS",
                style: TextStyle(color: Colors.purpleAccent, fontSize: 11, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              SwitchListTile(
                title: const Text("Mock Predictions Mode (Offline tests)"),
                value: _mockMode,
                activeColor: Colors.purpleAccent,
                onChanged: (val) {
                  setState(() {
                    _mockMode = val;
                  });
                },
              ),
              const SizedBox(height: 10),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    "Model Metadata Info:",
                    style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh, size: 18, color: Colors.purpleAccent),
                    onPressed: _fetchModelMetadata,
                  )
                ],
              ),
              const SizedBox(height: 8),
              if (_isLoadingMetadata)
                const Center(child: CircularProgressIndicator(color: Colors.purpleAccent))
              else if (_modelMetadata.containsKey("error"))
                Text(
                  _modelMetadata["error"],
                  style: const TextStyle(color: Colors.redAccent, fontSize: 11),
                )
              else if (_modelMetadata.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1F2937),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFF374151)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildMetadataTile("API Version", _modelMetadata["version"] ?? "N/A"),
                      const Divider(color: Color(0xFF374151)),
                      ...(_modelMetadata["models"] as Map<String, dynamic>).entries.map((entry) {
                        final m = entry.value;
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              m["name"] ?? entry.key.toUpperCase(),
                              style: const TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 4),
                            _buildMetadataTile("  Version", m["version"] ?? "N/A"),
                            if (m.containsKey("accuracy"))
                              _buildMetadataTile("  Accuracy", "${(m["accuracy"] * 100).toStringAsFixed(2)}%"),
                            if (m.containsKey("training_date"))
                              _buildMetadataTile("  Training Date", m["training_date"]),
                            if (m.containsKey("classes"))
                              _buildMetadataTile("  Supported Classes", (m["classes"] as List).join(", ")),
                            const SizedBox(height: 8),
                          ],
                        );
                      }),
                    ],
                  ),
                ),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildMetadataTile(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: RichText(
        text: TextSpan(
          style: const TextStyle(fontSize: 11, color: Colors.white),
          children: [
            TextSpan(text: "$label: ", style: const TextStyle(color: Colors.grey)),
            TextSpan(text: value, style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}