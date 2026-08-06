import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../triage/data/triage_backend_service.dart';
import '../data/prescription_backend_service.dart';

class PrescriptionScreen extends StatefulWidget {
  const PrescriptionScreen({super.key});

  @override
  State<PrescriptionScreen> createState() => _PrescriptionScreenState();
}

class _PrescriptionScreenState extends State<PrescriptionScreen> {
  final PrescriptionBackendService _service = const PrescriptionBackendService();
  final TriageBackendService _triageService = const TriageBackendService();
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _patientIdController = TextEditingController(text: 'P001');

  Uint8List? _imageBytes;
  bool _isLoading = false;
  String _statusText = 'Pick a prescription image to begin.';
  PrescriptionAuditResult? _result;

  // Triage State
  bool _loadingTriage = false;
  Map<String, dynamic>? _triageContextResult;
  Map<String, dynamic>? _triageSummaryResult;
  final Map<String, String> _patientAnswers = {};

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
        _triageContextResult = null;
        _triageSummaryResult = null;
        _patientAnswers.clear();
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
      final pId = _patientIdController.text.trim().isEmpty ? 'P001' : _patientIdController.text.trim();
      final result = await _service.auditPrescription(
        patientId: pId,
        imageBytes: imageBytes,
      );
      if (!mounted) return;
      setState(() {
        _result = result;
        _statusText = 'Audit complete. Fetching post-prescription triage questions...';
      });

      final drugNames = result.prescribedDrugs;
      if (drugNames.isNotEmpty) {
        _fetchPostScanTriage(pId, drugNames);
      }
    } catch (error) {
      if (mounted) setState(() => _statusText = 'Audit failed: $error');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _fetchPostScanTriage(String patientId, List<String> drugs) async {
    setState(() => _loadingTriage = true);

    final res = await _triageService.fetchTriageContext(
      patientId: patientId,
      drugs: drugs,
    );

    if (!mounted) return;
    setState(() {
      _loadingTriage = false;
      _triageContextResult = res;
      _statusText = 'Audit & Triage complete.';
    });
  }

  Future<void> _submitTriageAnswers() async {
    if (_triageContextResult == null) return;
    setState(() => _loadingTriage = true);

    final contexts = (_triageContextResult?['contexts'] as List?) ?? [];
    final contextStr = contexts.isNotEmpty ? contexts.first.toString() : 'Prescription Consultation';

    final res = await _triageService.fetchTriageSummary(
      patientId: _patientIdController.text.trim().isEmpty ? 'P001' : _patientIdController.text.trim(),
      drugs: _result?.prescribedDrugs ?? [],
      context: contextStr,
      answers: _patientAnswers,
    );

    if (!mounted) return;
    setState(() {
      _loadingTriage = false;
      _triageSummaryResult = res;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Rx Safety & Triage')),
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
            if (_loadingTriage)
              const Padding(
                padding: EdgeInsets.all(16),
                child: Center(child: CircularProgressIndicator()),
              ),
            if (_triageContextResult != null) ...[
              const SizedBox(height: 16),
              ..._buildTriageQuestionsView(),
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
          const _SectionTitle('OCR Extraction'),
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
          const _SectionTitle('Matched Drugs'),
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
          const _SectionTitle('Allergy Audit'),
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
          const _SectionTitle('Interaction Audit'),
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

  List<Widget> _buildTriageQuestionsView() {
    final res = _triageContextResult!;
    final bool cacheHit = res['cache_hit'] ?? false;
    final List questions = (res['question_tree'] as List?) ?? [];

    return [
      _Panel(
        title: '🩺 Post-Prescription Patient Triage',
        subtitle: cacheHit ? 'Reasoning loaded from local cache (0ms delay)' : 'Reasoning generated dynamically',
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
                    Text(questionText, style: const TextStyle(color: Color(0xFFD5E4FA), fontSize: 14, fontWeight: FontWeight.w600)),
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
