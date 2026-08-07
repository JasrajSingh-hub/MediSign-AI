import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/utils/web_camera_helper.dart';
import '../../triage/data/triage_backend_service.dart';
import '../data/emergency_backend_service.dart';

class EmergencyScreen extends StatefulWidget {
  const EmergencyScreen({super.key, required this.availableCameras});

  final List<CameraDescription> availableCameras;

  @override
  State<EmergencyScreen> createState() => _EmergencyScreenState();
}

class _EmergencyScreenState extends State<EmergencyScreen> {
  final EmergencyBackendService _service = const EmergencyBackendService();
  final TriageBackendService _triageService = const TriageBackendService();
  final MapController _mapController = MapController();

  CameraController? _cameraController;
  bool _cameraReady = false;
  bool _isPredicting = false;
  bool _backendOnline = false;
  bool _isLoadingHospitals = false;
  bool _locationReady = false;
  bool _pendingMapFit = false;
  String _statusText = 'Waiting...';
  EmergencyPrediction? _lastPrediction;
  List<NearbyHospital> _nearbyHospitals = [];
  Position? _currentPosition;

  // Triage state
  bool _loadingTriage = false;
  Map<String, dynamic>? _triageContextResult;
  Map<String, dynamic>? _triageSummaryResult;
  final Map<String, String> _patientAnswers = {};

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _checkBackendStatus();
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _mapController.dispose();
    super.dispose();
  }

  Future<void> _checkBackendStatus() async {
    final healthy = await _service.checkHealth();
    if (!mounted) return;
    setState(() {
      _backendOnline = healthy;
      if (!healthy) {
        _statusText = 'Emergency backend offline (localhost:5000)';
      }
    });
  }

  bool get _hasEmergencyRisk {
    final label = _lastPrediction?.label.toLowerCase() ?? '';
    return label.contains('pain') ||
        label.contains('help') ||
        label.contains('emergency') ||
        label.contains('distress') ||
        label.contains('hurt') ||
        label.contains('heart') ||
        label.contains('breathing') ||
        label.contains('knee');
  }

  Future<void> _initializeCamera() async {
    if (kIsWeb) {
      await requestWebCameraPermission();
    }

    List<CameraDescription> cameras = widget.availableCameras;
    try {
      cameras = await availableCameras();
    } catch (_) {}

    if (cameras.isEmpty) {
      if (mounted) setState(() => _statusText = 'No camera available.');
      return;
    }

    final controller = CameraController(cameras.first, ResolutionPreset.low, enableAudio: false);
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
      try {
        await controller.dispose();
      } catch (_) {}
      if (mounted) {
        setState(() => _statusText = 'Camera failed to initialize: $error');
      }
    }
  }

  Future<Uint8List?> _captureFrame() async {
    final controller = _cameraController;
    if (controller == null || !controller.value.isInitialized) return null;
    final picture = await controller.takePicture();
    final bytes = await picture.readAsBytes();
    if (!kIsWeb) {
      try {
        await File(picture.path).delete();
      } catch (_) {}
    }
    return bytes;
  }

  Future<void> _runPrediction() async {
    if (_isPredicting) return;
    setState(() {
      _isPredicting = true;
      _statusText = 'Analyzing frame...';
    });

    try {
      final bytes = await _captureFrame();
      if (bytes == null) throw Exception('Camera frame unavailable');
      final prediction = await _service.predictFromBytes(bytes);
      if (!mounted) return;
      setState(() {
        _lastPrediction = prediction;
        _statusText = prediction.isEmergency ? 'Emergency detected: ${prediction.label}' : 'No emergency detected';
      });

      if (prediction.isEmergency || _hasEmergencyRisk) {
        await _loadNearbyHospitals();
        await _triggerTriageForSign(prediction.label);
      }
    } catch (error) {
      if (mounted) {
        setState(() => _statusText = 'Prediction failed: $error');
      }
    } finally {
      if (mounted) setState(() => _isPredicting = false);
    }
  }

  Future<void> _triggerTriageForSign(String signLabel) async {
    setState(() {
      _loadingTriage = true;
      _triageContextResult = null;
      _triageSummaryResult = null;
      _patientAnswers.clear();
    });

    final res = await _triageService.fetchTriageContext(
      patientId: 'P001',
      emergencySign: signLabel,
    );

    if (!mounted) return;
    setState(() {
      _loadingTriage = false;
      _triageContextResult = res;
    });
  }

  Future<void> _submitTriageAnswers() async {
    if (_triageContextResult == null) return;
    setState(() => _loadingTriage = true);

    final contexts = (_triageContextResult?['contexts'] as List?) ?? [];
    final contextStr = contexts.isNotEmpty ? contexts.first.toString() : 'Emergency Triage';

    final res = await _triageService.fetchTriageSummary(
      patientId: 'P001',
      emergencySign: _lastPrediction?.label,
      context: contextStr,
      answers: _patientAnswers,
    );

    if (!mounted) return;
    setState(() {
      _loadingTriage = false;
      _triageSummaryResult = res;
    });
  }

  Future<void> _loadNearbyHospitals() async {
    if (_isLoadingHospitals) return;
    setState(() {
      _isLoadingHospitals = true;
      _statusText = 'Finding nearby hospitals...';
    });

    try {
      final position = await _determinePosition();
      final hospitals = await _service.fetchNearbyHospitals(latitude: position.latitude, longitude: position.longitude);
      if (!mounted) return;
      setState(() {
        _currentPosition = position;
        _nearbyHospitals = hospitals;
        _locationReady = true;
        _pendingMapFit = true;
        _statusText = hospitals.isEmpty ? 'Found 0 hospitals within 10 km' : 'Found ${hospitals.length} hospitals within 10 km';
      });
    } catch (error) {
      if (mounted) setState(() => _statusText = 'Hospital search failed: $error');
    } finally {
      if (mounted) setState(() => _isLoadingHospitals = false);
    }
  }

  Future<Position> _determinePosition() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) throw Exception('Location services are disabled');

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission != LocationPermission.whileInUse && permission != LocationPermission.always) {
      throw Exception('Location permission denied');
    }
    return Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.bestForNavigation);
  }

  void _fitMapToMarkers() {
    if (_currentPosition == null) return;
    final markers = <LatLng>[
      LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
      ..._nearbyHospitals.map((hospital) => LatLng(hospital.latitude, hospital.longitude)),
    ];
    if (markers.length == 1) {
      _mapController.move(markers.first, 14);
      return;
    }
    _mapController.fitCamera(
      CameraFit.bounds(bounds: LatLngBounds.fromPoints(markers), padding: const EdgeInsets.all(40), maxZoom: 15),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_pendingMapFit) {
      _pendingMapFit = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) _fitMapToMarkers();
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Code Alert & Sign Triage'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _StatusBanner(
              online: _backendOnline,
              text: _statusText,
              label: _lastPrediction == null ? 'No prediction yet' : 'Label: ${_lastPrediction!.label}',
            ),
            const SizedBox(height: 16),
            AspectRatio(
              aspectRatio: 3 / 4,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(22),
                child: Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF122031),
                    border: Border.all(color: Colors.white10),
                  ),
                  child: _cameraReady && _cameraController != null
                      ? FittedBox(
                          fit: BoxFit.cover,
                          child: SizedBox(
                            width: _cameraController!.value.previewSize?.height ?? 1,
                            height: _cameraController!.value.previewSize?.width ?? 1,
                            child: CameraPreview(_cameraController!),
                          ),
                        )
                      : const Center(child: CircularProgressIndicator()),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                FilledButton.icon(
                  onPressed: _isPredicting ? null : _runPrediction,
                  icon: _isPredicting ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.play_arrow),
                  label: Text(_isPredicting ? 'Analyzing...' : 'Run Sign Detection'),
                ),
                OutlinedButton.icon(
                  onPressed: () => _triggerTriageForSign('HEART'),
                  icon: const Icon(Icons.favorite),
                  label: const Text('Test HEART Sign'),
                ),
                OutlinedButton.icon(
                  onPressed: () => _triggerTriageForSign('BREATHING'),
                  icon: const Icon(Icons.air),
                  label: const Text('Test BREATHING Sign'),
                ),
                OutlinedButton.icon(
                  onPressed: () => _triggerTriageForSign('AMBULANCE'),
                  icon: const Icon(Icons.local_shipping),
                  label: const Text('Test AMBULANCE Sign'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_loadingTriage)
              const Padding(padding: EdgeInsets.all(16), child: Center(child: CircularProgressIndicator())),

            if (_triageContextResult != null) ..._buildTriageQuestionsView(),
            const SizedBox(height: 16),
            if (_locationReady) _buildHospitalMapCard(),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTriageQuestionsView() {
    final res = _triageContextResult!;
    final bool instantCritical = res['instant_critical'] ?? false;
    final List questions = (res['question_tree'] as List?) ?? [];

    if (instantCritical) {
      return [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF7F1D1D),
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('🚨 INSTANT CRITICAL EMERGENCY',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
              SizedBox(height: 6),
              Text('AMBULANCE Sign Detected! Bypassing questions and notifying emergency staff immediately.',
                  style: TextStyle(color: Colors.white70)),
            ],
          ),
        ),
      ];
    }

    return [
      Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF122031),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF0EA5A4)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🩺 Emergency Follow-up Questions (${_lastPrediction?.label ?? 'SIGN'} Detected):',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            ...questions.map((q) {
              final qMap = q as Map<String, dynamic>;
              final String qId = qMap['id'] ?? 'q';
              final String questionText = qMap['question'] ?? '';
              final List options = (qMap['options'] as List?) ?? [];

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(questionText, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: options.map((opt) {
                        final optStr = opt.toString();
                        final isSelected = _patientAnswers[qId] == optStr;
                        return ChoiceChip(
                          label: Text(optStr),
                          selected: isSelected,
                          selectedColor: const Color(0xFF10B981),
                          onSelected: (val) {
                            setState(() {
                              if (val) {
                                _patientAnswers[qId] = optStr;
                              } else {
                                _patientAnswers.remove(qId);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                  ],
                ),
              );
            }),
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed: _patientAnswers.isEmpty ? null : _submitTriageAnswers,
              icon: const Icon(Icons.assignment_turned_in),
              label: const Text('Submit Responses for Doctor Handoff'),
              style: FilledButton.styleFrom(backgroundColor: const Color(0xFF10B981)),
            ),
          ],
        ),
      ),
      if (_triageSummaryResult != null) ...[
        const SizedBox(height: 16),
        _buildDoctorSummaryCard(_triageSummaryResult!),
      ]
    ];
  }

  Widget _buildDoctorSummaryCard(Map<String, dynamic> res) {
    final String priority = res['priority'] ?? 'LOW';
    final bool redFlagAlert = res['red_flag_alert'] ?? false;
    final String summary = res['doctor_summary'] ?? '';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1024),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.redAccent),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('Doctor Handoff Report:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const Spacer(),
              Chip(
                label: Text(priority, style: const TextStyle(fontWeight: FontWeight.bold)),
                backgroundColor: priority == 'HIGH' ? Colors.red : Colors.amber,
              ),
            ],
          ),
          if (redFlagAlert) ...[
            const SizedBox(height: 4),
            const Text('🚨 RED FLAG ALERT DETECTED', style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold)),
          ],
          const Divider(height: 20),
          Text(summary, style: const TextStyle(fontSize: 13, height: 1.4)),
        ],
      ),
    );
  }

  Widget _buildHospitalMapCard() {
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
          const Text('Nearby hospitals', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          const SizedBox(height: 12),
          AspectRatio(
            aspectRatio: 16 / 10,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: FlutterMap(
                options: MapOptions(
                  initialCenter: _mapCenter,
                  initialZoom: 14,
                  interactionOptions: const InteractionOptions(flags: InteractiveFlag.pinchZoom | InteractiveFlag.drag),
                ),
                mapController: _mapController,
                children: [
                  TileLayer(
                    urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    userAgentPackageName: 'com.example.medisign_app',
                  ),
                  MarkerLayer(
                    markers: [
                      if (_currentPosition != null)
                        Marker(
                          point: LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
                          width: 40,
                          height: 40,
                          child: const Icon(Icons.my_location, color: Colors.redAccent, size: 34),
                        ),
                      ..._nearbyHospitals.map(
                        (hospital) => Marker(
                          point: LatLng(hospital.latitude, hospital.longitude),
                          width: 36,
                          height: 36,
                          child: const Icon(Icons.local_hospital, color: Colors.redAccent, size: 30),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          ..._nearbyHospitals.take(3).map(
                (hospital) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    '${hospital.name} - ${(hospital.distanceMeters / 1000).toStringAsFixed(1)} km away',
                    style: const TextStyle(color: Color(0xFFBBC9CD)),
                  ),
                ),
              ),
        ],
      ),
    );
  }

  LatLng get _mapCenter {
    if (_currentPosition != null) {
      return LatLng(_currentPosition!.latitude, _currentPosition!.longitude);
    }
    return LatLng(20.5937, 78.9629);
  }
}

class _StatusBanner extends StatelessWidget {
  const _StatusBanner({required this.online, required this.text, required this.label});

  final bool online;
  final String text;
  final String label;

  @override
  Widget build(BuildContext context) {
    final accent = online ? const Color(0xFF68F5B8) : const Color(0xFFEF4444);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF122031),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: accent.withOpacity(0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(text, style: TextStyle(color: accent, fontSize: 16, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text(label, style: const TextStyle(color: Color(0xFFBBC9CD))),
        ],
      ),
    );
  }
}
