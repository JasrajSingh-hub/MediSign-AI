import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:image/image.dart' as img_lib;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:vibration/vibration.dart';
import 'package:flutter_ringtone_player/flutter_ringtone_player.dart';

// Background isolate image compression worker
List<int> _resizeAndCompressImage(List<int> rawBytes) {
  try {
    final image = img_lib.decodeImage(Uint8List.fromList(rawBytes));
    if (image == null) return rawBytes;
    
    // Resize to smaller dimensions (width 256, maintaining aspect ratio)
    final resized = img_lib.copyResize(image, width: 256);
    
    // Compress to JPEG with 70% quality
    return img_lib.encodeJpg(resized, quality: 70);
  } catch (e) {
    return rawBytes; // Fallback to raw if decode fails
  }
}

class EmergencyScreen extends StatefulWidget {
  final List<CameraDescription> cameras;
  const EmergencyScreen({super.key, required this.cameras});

  @override
  State<EmergencyScreen> createState() => _EmergencyScreenState();
}

class _EmergencyScreenState extends State<EmergencyScreen> with SingleTickerProviderStateMixin {
  CameraController? _cameraController;
  bool _isCameraInitialized = false;
  bool _cameraPermissionDenied = false;

  // Configuration settings (loaded from SharedPreferences)
  String _backendUrl = 'http://127.0.0.1:8000';
  double _threshold = 0.80;
  int _intervalMs = 300;
  bool _enableAlarm = true;
  bool _enableVibration = true;
  bool _enableTts = true;
  bool _mockMode = false;
  bool _devModeUnlocked = false;

  // Active status states
  String _backendStatus = "Connecting..."; // "Online", "Offline", "Connecting"
  String _modelStatus = "Unknown"; // "Loaded", "Not Loaded", "Unknown"
  String _activePrediction = "Searching...";
  double _activeConfidence = 0.0;
  bool _emergencyAlertActive = false;
  int _apiLatencyMs = 0;
  
  // Timer and flow controls
  Timer? _processingTimer;
  Timer? _bannerFlashTimer;
  bool _isProcessingFrame = false;
  bool _bannerFlashState = false;
  
  // TTS Engine
  final FlutterTts _ttsEngine = FlutterTts();
  String? _lastSpokenAlert;
  DateTime? _lastAlertTime;

  // History list (Last 20)
  List<Map<String, dynamic>> _predictionHistory = [];
  
  // Temporal consensus filters
  int _consecutiveEmergencyFrames = 0;
  int _consecutiveSafeFrames = 0;

  // Animation controller for visual alerts
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    )..repeat(reverse: true);
    
    _loadSettings().then((_) {
      _initializeCamera();
      _startBackendHealthCheck();
    });
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _backendUrl = prefs.getString('emergency_url') ?? 'http://127.0.0.1:8000';
      _threshold = prefs.getDouble('confidence_threshold') ?? 0.80;
      _intervalMs = prefs.getInt('frame_interval_ms') ?? 300;
      _enableAlarm = prefs.getBool('enable_alarm') ?? true;
      _enableVibration = prefs.getBool('enable_vibration') ?? true;
      _enableTts = prefs.getBool('enable_tts') ?? true;
      _mockMode = prefs.getBool('mock_mode') ?? false;
      _devModeUnlocked = prefs.getBool('dev_mode_unlocked') ?? false;
      
      // Load history
      final historyRaw = prefs.getStringList('prediction_history') ?? [];
      _predictionHistory = historyRaw.map((item) {
        try {
          return jsonDecode(item) as Map<String, dynamic>;
        } catch (_) {
          return <String, dynamic>{};
        }
      }).where((element) => element.isNotEmpty).toList();
    });
  }

  Future<void> _saveHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final historyRaw = _predictionHistory.map((item) => jsonEncode(item)).toList();
    await prefs.setStringList('prediction_history', historyRaw);
  }

  void _initializeCamera() async {
    if (widget.cameras.isEmpty) {
      setState(() {
        _cameraPermissionDenied = true;
      });
      return;
    }

    _cameraController = CameraController(
      widget.cameras[0],
      ResolutionPreset.low,
      enableAudio: false,
    );

    try {
      await _cameraController!.initialize();
      if (!mounted) return;
      setState(() {
        _isCameraInitialized = true;
        _cameraPermissionDenied = false;
      });
      _startCaptureLoop();
    } catch (e) {
      setState(() {
        _cameraPermissionDenied = true;
      });
    }
  }

  void _startCaptureLoop() {
    _processingTimer?.cancel();
    _processingTimer = Timer.periodic(Duration(milliseconds: _intervalMs), (timer) async {
      if (_isProcessingFrame || 
          _cameraController == null || 
          !_cameraController!.value.isInitialized || 
          _cameraController!.value.isTakingPicture) {
        return;
      }

      setState(() {
        _isProcessingFrame = true;
      });

      await _captureAndProcessFrame();

      if (mounted) {
        setState(() {
          _isProcessingFrame = false;
        });
      }
    });
  }

  Future<void> _captureAndProcessFrame() async {
    if (_mockMode) {
      await Future.delayed(const Duration(milliseconds: 100));
      // Simulate random mock predictions
      final isAlert = DateTime.now().second % 10 == 0;
      final label = isAlert ? "help" : "No hand";
      final confidence = isAlert ? 0.88 : 0.0;
      _handlePredictionResult(label, confidence, true);
      return;
    }

    try {
      final picture = await _cameraController!.takePicture();
      
      // 1. Read raw bytes directly from cross-platform XFile
      final rawBytes = await picture.readAsBytes();
      
      // 2. Clear temp file immediately on native platforms
      if (!kIsWeb) {
        try {
          await File(picture.path).delete();
        } catch (_) {}
      }

      // 3. Compress in background Isolate
      final compressedBytes = await compute(_resizeAndCompressImage, rawBytes);
      
      // 4. Send base64 payload
      final base64Image = base64Encode(compressedBytes);
      
      final startTime = DateTime.now();
      final url = Uri.parse('$_backendUrl/predict');
      
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: {"image_base64": "data:image/jpeg;base64,$base64Image"},
      ).timeout(const Duration(milliseconds: 3000));

      final endTime = DateTime.now();
      
      if (mounted) {
        setState(() {
          _apiLatencyMs = endTime.difference(startTime).inMilliseconds;
          _backendStatus = "Online";
        });
      }

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final label = data['label'] ?? "No hand";
        final confidence = (data['confidence'] as num?)?.toDouble() ?? 0.0;
        final isEmergency = data['is_emergency'] as bool? ?? false;
        _handlePredictionResult(label, confidence, isEmergency);
      } else if (response.statusCode == 422) {
        try {
          final data = jsonDecode(response.body);
          final detail = data['detail'] ?? "";
          if (detail.toString().contains("No hand")) {
            _handlePredictionResult("No hand", 0.0, false);
          } else {
            _handlePredictionResult("API Error", 0.0, false);
          }
        } catch (_) {
          _handlePredictionResult("API Error", 0.0, false);
        }
      } else {
        _handlePredictionResult("API Error", 0.0, false);
      }
    } on TimeoutException {
      if (mounted) {
        setState(() {
          _backendStatus = "Offline";
          _activePrediction = "Request Timeout";
          _activeConfidence = 0.0;
        });
      }
    } catch (e, stack) {
      print("Prediction call error: $e\n$stack");
      if (mounted) {
        setState(() {
          _backendStatus = "Offline";
          _activePrediction = "Connection Offline";
          _activeConfidence = 0.0;
        });
      }
    }
  }

  void _handlePredictionResult(String label, double confidence, bool isEmergency) {
    if (!mounted) return;
    
    setState(() {
      _activePrediction = label;
      _activeConfidence = confidence;
    });

    final now = DateTime.now();
    
    // Add to history if prediction changed or is positive and time interval passed
    if (_predictionHistory.isEmpty || 
        _predictionHistory.first['label'] != label || 
        (isEmergency && now.difference(_lastAlertTime ?? DateTime(0)).inSeconds > 3)) {
      
      _predictionHistory.insert(0, {
        "timestamp": "${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:${now.second.toString().padLeft(2, '0')}",
        "label": label,
        "confidence": confidence,
      });

      if (_predictionHistory.length > 20) {
        _predictionHistory.removeLast();
      }
      _saveHistory();
    }

    // Check if the confidence exceeds the custom threshold with temporal consensus
    if (isEmergency && confidence >= _threshold) {
      _consecutiveEmergencyFrames++;
      _consecutiveSafeFrames = 0;
      if (_consecutiveEmergencyFrames >= 3) {
        _triggerAlertFlow(label);
      }
    } else {
      _consecutiveSafeFrames++;
      _consecutiveEmergencyFrames = 0;
      if (_consecutiveSafeFrames >= 3) {
        _cancelAlertFlow();
      }
    }
  }

  void _triggerAlertFlow(String label) {
    if (_emergencyAlertActive) return;

    setState(() {
      _emergencyAlertActive = true;
    });

    _lastAlertTime = DateTime.now();

    // Start Flashing Banner Timer
    _bannerFlashTimer?.cancel();
    _bannerFlashTimer = Timer.periodic(const Duration(milliseconds: 350), (timer) {
      setState(() {
        _bannerFlashState = !_bannerFlashState;
      });
    });

    // 1. Audio Alarm Playback
    if (_enableAlarm) {
      try {
        FlutterRingtonePlayer.playAlarm();
      } catch (_) {}
    }

    // 2. Haptic Vibration Alert
    if (_enableVibration) {
      Vibration.hasVibrator().then((hasVib) {
        if (hasVib == true) {
          Vibration.vibrate(pattern: [500, 200, 500, 200], repeat: 0);
        }
      });
    }

    // 3. Text-to-Speech Announcement
    if (_enableTts && _lastSpokenAlert != label) {
      _lastSpokenAlert = label;
      _ttsEngine.speak("Emergency detected: $label. Assistance needed.");
    }
  }

  void _cancelAlertFlow() {
    if (!_emergencyAlertActive) return;

    setState(() {
      _emergencyAlertActive = false;
      _bannerFlashState = false;
    });

    _bannerFlashTimer?.cancel();
    
    // Stop Alarm Sound
    try {
      FlutterRingtonePlayer.stop();
    } catch (_) {}

    // Stop Vibration
    try {
      Vibration.cancel();
    } catch (_) {}

    _lastSpokenAlert = null;
  }

  void _startBackendHealthCheck() {
    // Poll backend status every 5 seconds
    Timer.periodic(const Duration(seconds: 5), (timer) async {
      if (!mounted) {
        timer.cancel();
        return;
      }
      if (_mockMode) {
        setState(() {
          _backendStatus = "Online";
          _modelStatus = "Loaded (Mock)";
        });
        return;
      }

      try {
        final res = await http.get(Uri.parse('$_backendUrl/status')).timeout(const Duration(seconds: 5));
        if (res.statusCode == 200) {
          final data = jsonDecode(res.body);
          setState(() {
            _backendStatus = "Online";
            _modelStatus = data['model_loaded'] == true ? "Loaded" : "Not Loaded";
          });
        }
      } catch (e, stack) {
        print("Backend health check error: $e\n$stack");
        setState(() {
          _backendStatus = "Offline";
          _modelStatus = "Offline";
        });
      }
    });
  }

  @override
  void dispose() {
    _cancelAlertFlow();
    _processingTimer?.cancel();
    _bannerFlashTimer?.cancel();
    _cameraController?.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final alertColor = _bannerFlashState 
        ? const Color(0xFFEF4444) // Bright Red
        : const Color(0xFFF59E0B); // Amber Orange

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Flashing Emergency Alert Banner
            if (_emergencyAlertActive)
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                color: alertColor,
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: Colors.white, size: 28),
                    const SizedBox(width: 12),
                    Text(
                      "EMERGENCY ACTIVE: ${_activePrediction.toUpperCase()}",
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.2
                      ),
                    ),
                  ],
                ),
              ),

            // Top Section: Live Camera Feed with Status Indicators
            Expanded(
              flex: 5,
              child: Container(
                margin: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF1F2937),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _emergencyAlertActive ? alertColor : const Color(0xFF374151),
                    width: _emergencyAlertActive ? 4 : 1,
                  ),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(14),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      // Camera Preview or Fallbacks
                      if (_cameraPermissionDenied)
                        const Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.camera_alt_outlined, size: 64, color: Colors.redAccent),
                              SizedBox(height: 12),
                              Text(
                                "Camera Permission Denied",
                                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                              SizedBox(height: 4),
                              Text(
                                "Grant camera permissions in device settings.",
                                style: TextStyle(color: Colors.grey, fontSize: 12),
                              )
                            ],
                          ),
                        )
                      else if (_isCameraInitialized && _cameraController != null)
                        CameraPreview(_cameraController!)
                      else
                        const Center(
                          child: CircularProgressIndicator(color: Colors.redAccent),
                        ),

                      // Status Overlay HUD (Glassmorphism Effect)
                      Positioned(
                        top: 12,
                        left: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.6),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    width: 8,
                                    height: 8,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: _backendStatus == "Online" 
                                          ? Colors.greenAccent 
                                          : _backendStatus == "Connecting..." 
                                              ? Colors.amberAccent 
                                              : Colors.redAccent,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    "Server: $_backendStatus",
                                    style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                "Model: $_modelStatus",
                                style: const TextStyle(color: Colors.grey, fontSize: 10),
                              ),
                            ],
                          ),
                        ),
                      ),

                      // Performance HUD (Visible in Developer Mode)
                      if (_devModeUnlocked)
                        Positioned(
                          top: 12,
                          right: 12,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.6),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  "Latency: ${_apiLatencyMs}ms",
                                  style: const TextStyle(color: Colors.cyanAccent, fontSize: 10, fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  "Interval: ${_intervalMs}ms",
                                  style: const TextStyle(color: Colors.grey, fontSize: 9),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  _mockMode ? "MOCK DATA ACTIVE" : "REAL DATA",
                                  style: TextStyle(
                                    color: _mockMode ? Colors.amber : Colors.green,
                                    fontSize: 8, 
                                    fontWeight: FontWeight.bold
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),

            // Middle Section: Active Prediction Output
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1F2937),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF374151)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          "CURRENT EMERGENCY GESTURE:",
                          style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _activePrediction == "No hand" ? "No Hand Detected" : _activePrediction.toUpperCase(),
                          style: TextStyle(
                            color: _activePrediction == "No hand" 
                                ? Colors.grey 
                                : _emergencyAlertActive 
                                    ? Colors.redAccent 
                                    : Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  // Confidence Indicator Ring
                  Container(
                    width: 60,
                    height: 60,
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.black.withOpacity(0.2),
                    ),
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        CircularProgressIndicator(
                          value: _activeConfidence,
                          strokeWidth: 5,
                          backgroundColor: const Color(0xFF374151),
                          color: _activeConfidence >= _threshold 
                              ? Colors.redAccent 
                              : Colors.greenAccent,
                        ),
                        Center(
                          child: Text(
                            "${(_activeConfidence * 100).toStringAsFixed(0)}%",
                            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                          ),
                        )
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Bottom Section: History List (Last 20)
            Expanded(
              flex: 4,
              child: Container(
                margin: const EdgeInsets.fromLTRB(12, 12, 12, 0),
                padding: const EdgeInsets.all(16),
                decoration: const BoxDecoration(
                  color: Color(0xFF111827),
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(16),
                    topRight: Radius.circular(16),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          "PREDICTION LOG (LAST 20)",
                          style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                        if (_predictionHistory.isNotEmpty)
                          GestureDetector(
                            onTap: () {
                              setState(() {
                                _predictionHistory.clear();
                              });
                              _saveHistory();
                            },
                            child: const Text(
                              "Clear Log",
                              style: TextStyle(color: Colors.redAccent, fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          )
                      ],
                    ),
                    const SizedBox(height: 10),
                    Expanded(
                      child: _predictionHistory.isEmpty
                          ? const Center(
                              child: Text(
                                "No history logs yet.",
                                style: TextStyle(color: Colors.grey, fontSize: 12),
                              ),
                            )
                          : ListView.builder(
                              itemCount: _predictionHistory.length,
                              itemBuilder: (context, index) {
                                final log = _predictionHistory[index];
                                final isAlert = log['label'] != "No hand" && 
                                    log['label'] != "Searching..." && 
                                    log['label'] != "API Error" && 
                                    (log['confidence'] ?? 0.0) >= _threshold;
                                
                                return Container(
                                  margin: const EdgeInsets.symmetric(vertical: 4),
                                  padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF1F2937),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(
                                      color: isAlert ? Colors.redAccent.withOpacity(0.3) : const Color(0xFF374151),
                                    ),
                                  ),
                                  child: Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          Icon(
                                            isAlert ? Icons.warning_amber : Icons.history_toggle_off,
                                            color: isAlert ? Colors.redAccent : Colors.grey,
                                            size: 16,
                                          ),
                                          const SizedBox(width: 8),
                                          Text(
                                            (log['label'] as String).toUpperCase(),
                                            style: TextStyle(
                                              color: isAlert ? Colors.redAccent : Colors.white,
                                              fontSize: 12,
                                              fontWeight: FontWeight.bold
                                            ),
                                          ),
                                        ],
                                      ),
                                      Row(
                                        children: [
                                          Text(
                                            "${((log['confidence'] as num?)?.toDouble() ?? 0.0 * 100).toStringAsFixed(0)}% confidence",
                                            style: const TextStyle(color: Colors.grey, fontSize: 10),
                                          ),
                                          const SizedBox(width: 12),
                                          Text(
                                            log['timestamp'] ?? "",
                                            style: const TextStyle(color: Colors.grey, fontSize: 10),
                                          ),
                                        ],
                                      )
                                    ],
                                  ),
                                );
                              },
                            ),
                    ),
                  ],
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
