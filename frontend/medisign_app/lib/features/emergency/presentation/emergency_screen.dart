import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../data/emergency_backend_service.dart';

class EmergencyScreen extends StatefulWidget {
  const EmergencyScreen({super.key, required this.availableCameras});

  final List<CameraDescription> availableCameras;

  @override
  State<EmergencyScreen> createState() => _EmergencyScreenState();
}

class _EmergencyScreenState extends State<EmergencyScreen> {
  final EmergencyBackendService _service = const EmergencyBackendService();
  CameraController? _cameraController;
  bool _cameraReady = false;
  bool _isPredicting = false;
  bool _backendOnline = false;
  String _statusText = 'Waiting...';
  EmergencyPrediction? _lastPrediction;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _checkBackend();
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }

  Future<void> _checkBackend() async {
    try {
      final online = await _service.checkHealth();
      if (!mounted) {
        return;
      }
      setState(() {
        _backendOnline = online;
        _statusText = online ? 'Backend online' : 'Backend offline';
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _backendOnline = false;
        _statusText = 'Backend offline';
      });
    }
  }

  Future<void> _initializeCamera() async {
    if (widget.availableCameras.isEmpty) {
      setState(() {
        _statusText = 'No camera available';
      });
      return;
    }

    final controller = CameraController(
      widget.availableCameras.first,
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
        _cameraReady = true;
      });
    } catch (error) {
      debugPrint('Emergency camera init error: $error');
      await controller.dispose();
      if (mounted) {
        setState(() {
          _statusText = 'Camera failed to initialize';
        });
      }
    }
  }

  Future<Uint8List?> _captureFrame() async {
    final controller = _cameraController;
    if (controller == null || !controller.value.isInitialized) {
      debugPrint('Emergency camera capture skipped: controller unavailable or not initialized');
      return null;
    }

    debugPrint('Emergency camera capture started');
    final picture = await controller.takePicture();
    final bytes = await picture.readAsBytes();
    if (!kIsWeb) {
      try {
        await File(picture.path).delete();
      } catch (_) {}
    }
    debugPrint('Emergency camera capture complete (bytes=${bytes.length})');
    return bytes;
  }

  Future<void> _runPrediction() async {
    if (_isPredicting) {
      return;
    }

    setState(() {
      _isPredicting = true;
      _statusText = 'Analyzing frame...';
    });

    try {
      final bytes = await _captureFrame();
      if (bytes == null) {
        throw Exception('Camera frame unavailable');
      }
      debugPrint('Emergency prediction sending request');
      final prediction = await _service.predictFromBytes(bytes);
      if (!mounted) {
        return;
      }
      setState(() {
        _lastPrediction = prediction;
        _statusText = prediction.isEmergency
            ? 'Emergency detected: ${prediction.label}'
            : 'No emergency detected';
      });
    } catch (error) {
      debugPrint('Emergency prediction error: $error');
      if (mounted) {
        setState(() {
          _statusText = 'Prediction failed: $error';
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isPredicting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergency AI Model'),
        backgroundColor: const Color(0xFF111827),
      ),
      backgroundColor: const Color(0xFF0B1220),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(18),
                  child: Container(
                    color: const Color(0xFF111827),
                    child: _cameraReady && _cameraController != null
                        ? CameraPreview(_cameraController!)
                        : const Center(
                            child: CircularProgressIndicator(color: Colors.redAccent),
                          ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: _backendOnline ? Colors.greenAccent : Colors.redAccent),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _statusText,
                      style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _lastPrediction == null
                          ? 'No prediction yet'
                          : 'Label: ${_lastPrediction!.label} | Confidence: ${(_lastPrediction!.confidence * 100).toStringAsFixed(1)}%',
                      style: const TextStyle(color: Colors.grey, fontSize: 13),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _isPredicting ? null : _runPrediction,
                        icon: _isPredicting
                            ? const SizedBox(
                                width: 14,
                                height: 14,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                              )
                            : const Icon(Icons.play_arrow),
                        label: Text(_isPredicting ? 'Analyzing...' : 'Run Emergency Detection'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
