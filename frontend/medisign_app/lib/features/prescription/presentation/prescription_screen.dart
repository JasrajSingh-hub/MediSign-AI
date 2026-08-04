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
      if (image == null) return;
      final bytes = await image.readAsBytes();
      setState(() {
        _imageBytes = bytes;
        _statusText = 'Image loaded. Ready to audit.';
        _result = null;
      });
    } catch (error) {
      setState(() => _statusText = 'Failed to load image: $error');
    }
  }

  Future<void> _runAudit() async {
    final imageBytes = _imageBytes;
    if (imageBytes == null) {
      setState(() => _statusText = 'Please select an image first.');
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
      if (!mounted) return;
      setState(() {
        _result = result;
        _statusText = 'Audit complete.';
      });
    } catch (error) {
      if (mounted) setState(() => _statusText = 'Audit failed: $error');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Rx Safety')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _Panel(
              title: 'Patient Details',
              subtitle: _statusText,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    controller: _patientIdController,
                    decoration: const InputDecoration(labelText: 'Patient ID', hintText: 'Enter patient id'),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    children: [
                      FilledButton.icon(
                        onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                        icon: const Icon(Icons.photo_camera),
                        label: const Text('Camera'),
                      ),
                      OutlinedButton.icon(
                        onPressed: _isLoading ? null : () => _pickImage(ImageSource.gallery),
                        icon: const Icon(Icons.photo_library),
                        label: const Text('Gallery'),
                      ),
                      FilledButton.icon(
                        onPressed: _isLoading ? null : _runAudit,
                        icon: _isLoading
                            ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                            : const Icon(Icons.play_arrow),
                        label: Text(_isLoading ? 'Auditing...' : 'Run Audit'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            if (_imageBytes != null)
              _Panel(
                title: 'Scan Preview',
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(14),
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
    final interactionAudit = result.interactionAudit;
    return _Panel(
      title: 'Analysis Results',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _SectionTitle('OCR Extraction'),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF0E1C2D),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.white10),
            ),
            child: Text(
              result.rawText.isEmpty ? 'No text returned' : result.rawText,
              style: const TextStyle(color: Color(0xFFD5E4FA), height: 1.4),
            ),
          ),
          const SizedBox(height: 14),
          _SectionTitle('Matched Drugs'),
          const SizedBox(height: 8),
          if (result.matchedDrugs.isEmpty)
            const Text('No drug names matched from the image.', style: TextStyle(color: Color(0xFFBBC9CD)))
          else
            ...result.matchedDrugs.map((drug) {
              final confidence = (drug['confidence'] as num?)?.toDouble() ?? 0.0;
              final status = drug['status']?.toString() ?? 'unknown';
              final brand = drug['brand']?.toString() ?? '';
              return _InfoCard(
                title: drug['matched_drug']?.toString() ?? 'Unknown',
                accent: status == 'confident' ? const Color(0xFF68F5B8) : const Color(0xFFFFC857),
                subtitle: [
                  if (brand.isNotEmpty) 'Brand: $brand',
                  'Input token: ${drug['input_token'] ?? ''}',
                  'Confidence: ${confidence.toStringAsFixed(1)}%',
                  'Status: $status',
                ].join('\n'),
              );
            }),
          const SizedBox(height: 14),
          _SectionTitle('Allergy Audit'),
          const SizedBox(height: 8),
          _StatRow(label: 'Safe drugs', value: '${result.safeDrugs.length}', color: const Color(0xFF68F5B8)),
          const SizedBox(height: 8),
          if (result.allergyConflicts.isEmpty)
            const Text('No allergy conflicts found.', style: TextStyle(color: Color(0xFFBBC9CD)))
          else
            ...result.allergyConflicts.map((conflict) {
              final alternatives = List<dynamic>.from(conflict['alternatives'] ?? const []);
              return _InfoCard(
                title: '${conflict['drug'] ?? 'Unknown'}',
                accent: const Color(0xFFEF4444),
                subtitle: [
                  'Matched class: ${conflict['matched_class'] ?? ''}',
                  'Allergy class: ${conflict['allergy_class'] ?? ''}',
                  if (alternatives.isNotEmpty) 'Alternatives: ${alternatives.map((alt) => alt['alternative_drug']).join(', ')}',
                ].join('\n'),
              );
            }),
          const SizedBox(height: 14),
          _SectionTitle('Interaction Audit'),
          const SizedBox(height: 8),
          _StatRow(
            label: 'Safe combinations',
            value: '${List<String>.from(interactionAudit['safe'] ?? const []).length}',
            color: const Color(0xFF22D3EE),
          ),
          const SizedBox(height: 8),
          if (result.interactionConflicts.isEmpty)
            const Text('No interaction conflicts found.', style: TextStyle(color: Color(0xFFBBC9CD)))
          else
            ...result.interactionConflicts.map((interaction) {
              return _InfoCard(
                title: '${interaction['drug_a']} + ${interaction['drug_b']}',
                accent: _severityColor(interaction['severity']?.toString() ?? ''),
                subtitle: [
                  'Severity: ${interaction['severity'] ?? ''}',
                  'Description: ${interaction['description'] ?? ''}',
                  'Mechanism: ${interaction['mechanism'] ?? ''}',
                ].join('\n'),
              );
            }),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) => Text(title, style: const TextStyle(color: Color(0xFFD5E4FA), fontSize: 15, fontWeight: FontWeight.w700));

  Color _severityColor(String severity) {
    switch (severity.toUpperCase()) {
      case 'CONTRAINDICATED':
      case 'MAJOR':
        return const Color(0xFFEF4444);
      case 'MODERATE':
        return const Color(0xFFFFC857);
      default:
        return const Color(0xFF68F5B8);
    }
  }
}

class _Panel extends StatelessWidget {
  const _Panel({required this.title, required this.child, this.subtitle});

  final String title;
  final String? subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
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
          Text(title, style: const TextStyle(color: Color(0xFFD5E4FA), fontSize: 18, fontWeight: FontWeight.w700)),
          if (subtitle != null) ...[
            const SizedBox(height: 6),
            Text(subtitle!, style: const TextStyle(color: Color(0xFFBBC9CD), fontSize: 13)),
          ],
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.title);

  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(title, style: const TextStyle(color: Color(0xFFD5E4FA), fontSize: 14, fontWeight: FontWeight.w700));
  }
}

class _StatRow extends StatelessWidget {
  const _StatRow({required this.label, required this.value, required this.color});

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withOpacity(0.25)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Color(0xFFBBC9CD))),
          Text(value, style: TextStyle(color: color, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.title, required this.subtitle, required this.accent});

  final String title;
  final String subtitle;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: accent.withOpacity(0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: accent.withOpacity(0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(color: accent, fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          Text(subtitle, style: const TextStyle(color: Color(0xFFBBC9CD), height: 1.35)),
        ],
      ),
    );
  }
}
