import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../data/prescription_backend_service.dart';

class PrescriptionScreen extends StatefulWidget {
  const PrescriptionScreen({super.key});

  @override
  State<PrescriptionScreen> createState() => _PrescriptionScreenState();
}

class _PrescriptionScreenState extends State<PrescriptionScreen> {
  final PrescriptionBackendService _service = const PrescriptionBackendService();
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _patientIdController = TextEditingController(text: 'P001');

  Uint8List? _imageBytes;
  bool _isLoading = false;
  String _statusText = 'Pick a prescription image to begin.';
  PrescriptionAuditResult? _result;

  @override
  void dispose() {
    _patientIdController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final image = await _picker.pickImage(source: source, imageQuality: 85);
      if (image == null) {
        return;
      }
      final bytes = await image.readAsBytes();
      setState(() {
        _imageBytes = bytes;
        _statusText = 'Image loaded. Ready to audit.';
        _result = null;
      });
    } catch (error) {
      setState(() {
        _statusText = 'Failed to load image: $error';
      });
    }
  }

  Future<void> _runAudit() async {
    final imageBytes = _imageBytes;
    if (imageBytes == null) {
      setState(() {
        _statusText = 'Please select an image first.';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _statusText = 'Running prescription audit...';
    });

    try {
      await _service.checkHealth();
      final result = await _service.auditPrescription(
        patientId: _patientIdController.text.trim().isEmpty ? 'P001' : _patientIdController.text.trim(),
        imageBytes: imageBytes,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _result = result;
        _statusText = 'Audit complete.';
      });
    } catch (error) {
      if (mounted) {
        setState(() {
          _statusText = 'Audit failed: $error';
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Prescription Safety'),
        backgroundColor: const Color(0xFF111827),
      ),
      backgroundColor: const Color(0xFF0B1220),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF111827),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.cyanAccent.withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Patient ID',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _patientIdController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Enter patient id',
                      hintStyle: const TextStyle(color: Colors.grey),
                      filled: true,
                      fillColor: const Color(0xFF1F2937),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      ElevatedButton.icon(
                        onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                        icon: const Icon(Icons.photo_camera),
                        label: const Text('Camera'),
                      ),
                      ElevatedButton.icon(
                        onPressed: _isLoading ? null : () => _pickImage(ImageSource.gallery),
                        icon: const Icon(Icons.photo_library),
                        label: const Text('Gallery'),
                      ),
                      ElevatedButton.icon(
                        onPressed: _isLoading ? null : _runAudit,
                        icon: _isLoading
                            ? const SizedBox(
                                width: 14,
                                height: 14,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                              )
                            : const Icon(Icons.play_arrow),
                        label: Text(_isLoading ? 'Auditing...' : 'Run Audit'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(_statusText, style: const TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 16),
            if (_imageBytes != null)
              Container(
                height: 220,
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.memory(_imageBytes!, fit: BoxFit.cover),
                ),
              ),
            if (_result != null) ...[
              const SizedBox(height: 16),
              _buildResultPanel(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResultPanel() {
    final result = _result!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.greenAccent.withOpacity(0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('OCR Result', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(result.rawText.isEmpty ? 'No text returned' : result.rawText, style: const TextStyle(color: Colors.white70)),
          const SizedBox(height: 12),
          Text('Drugs: ${result.prescribedDrugs.join(', ')}', style: const TextStyle(color: Colors.white)),
          const SizedBox(height: 12),
          Text('Allergy conflicts: ${result.allergyConflicts.length}', style: const TextStyle(color: Colors.white)),
          Text('Interaction conflicts: ${result.interactionConflicts.length}', style: const TextStyle(color: Colors.white)),
        ],
      ),
    );
  }
}
