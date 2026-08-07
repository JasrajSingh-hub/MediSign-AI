import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class TriageBackendService {
  const TriageBackendService({this.baseUrl = 'http://localhost:5000'});

  final String baseUrl;

  Future<Map<String, dynamic>?> fetchTriageContext({
    required String patientId,
    List<String> drugs = const [],
    String? emergencySign,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/triage/context');
      final resp = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'patient_id': patientId,
              'drugs': drugs,
              'emergency_sign': (emergencySign != null && emergencySign.toUpperCase() != 'NONE')
                  ? emergencySign.toUpperCase()
                  : null,
            }),
          )
          .timeout(const Duration(seconds: 15));

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body) as Map<String, dynamic>;
      }
    } catch (e) {
      debugPrint('fetchTriageContext error: $e');
    }
    return null;
  }

  Future<Map<String, dynamic>?> fetchTriageSummary({
    required String patientId,
    List<String> drugs = const [],
    String? emergencySign,
    String context = 'General Consultation',
    required Map<String, String> answers,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/triage/summary');
      final resp = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'patient_id': patientId,
              'drugs': drugs,
              'emergency_sign': (emergencySign != null && emergencySign.toUpperCase() != 'NONE')
                  ? emergencySign.toUpperCase()
                  : null,
              'context': context,
              'answers': answers,
            }),
          )
          .timeout(const Duration(seconds: 15));

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body) as Map<String, dynamic>;
      }
    } catch (e) {
      debugPrint('fetchTriageSummary error: $e');
    }
    return null;
  }
}
