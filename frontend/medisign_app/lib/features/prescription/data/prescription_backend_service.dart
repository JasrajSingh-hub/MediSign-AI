import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../../../core/config/backend_endpoints.dart';

class PrescriptionAuditResult {
  const PrescriptionAuditResult({
    required this.patientId,
    required this.rawText,
    required this.prescribedDrugs,
    required this.matchedDrugs,
    required this.safeDrugs,
    required this.allergyConflicts,
    required this.interactionConflicts,
    required this.allergyAudit,
    required this.interactionAudit,
  });

  final String patientId;
  final String rawText;
  final List<String> prescribedDrugs;
  final List<Map<String, dynamic>> matchedDrugs;
  final List<dynamic> safeDrugs;
  final List<dynamic> allergyConflicts;
  final List<dynamic> interactionConflicts;
  final Map<String, dynamic> allergyAudit;
  final Map<String, dynamic> interactionAudit;

  factory PrescriptionAuditResult.fromJson(Map<String, dynamic> json) {
    final audit = Map<String, dynamic>.from(json['audit'] ?? const {});
    final allergy = Map<String, dynamic>.from(audit['allergy'] ?? const {});
    final interactions = Map<String, dynamic>.from(audit['interactions'] ?? const {});

    return PrescriptionAuditResult(
      patientId: json['patient_id']?.toString() ?? '',
      rawText: json['raw_text']?.toString() ?? '',
      prescribedDrugs: List<String>.from(json['prescribed_drugs'] ?? const []),
      matchedDrugs: List<dynamic>.from(json['matched_drugs'] ?? const [])
          .map((item) => Map<String, dynamic>.from(item as Map))
          .toList(),
      safeDrugs: List<dynamic>.from(
        (allergy['safe'] ?? const []) as List,
      ),
      allergyConflicts: List<dynamic>.from(allergy['conflicts'] ?? const []),
      interactionConflicts: List<dynamic>.from(interactions['interactions'] ?? const []),
      allergyAudit: allergy,
      interactionAudit: interactions,
    );
  }
}

class PrescriptionBackendService {
  const PrescriptionBackendService();

  Future<Map<String, dynamic>> checkHealth() async {
    final response = await http.get(Uri.parse(BackendEndpoints.moduleBHealth));
    if (response.statusCode != 200) {
      throw Exception('Prescription backend unavailable');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<PrescriptionAuditResult> auditPrescription({
    required String patientId,
    required Uint8List imageBytes,
  }) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse(BackendEndpoints.moduleBOcrAudit),
    );
    request.fields['patient_id'] = patientId;
    request.files.add(
      http.MultipartFile.fromBytes(
        'image',
        imageBytes,
        filename: 'prescription.jpg',
        contentType: MediaType('image', 'jpeg'),
      ),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    if (response.statusCode != 200) {
      String message = 'Prescription audit failed';
      try {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        message = body['detail']?.toString() ?? message;
      } catch (_) {
        message = response.body;
      }
      throw Exception(message);
    }

    return PrescriptionAuditResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
