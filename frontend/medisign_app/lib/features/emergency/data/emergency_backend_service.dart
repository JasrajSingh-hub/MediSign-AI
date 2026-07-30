import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../../../core/config/backend_endpoints.dart';

class EmergencyPrediction {
  const EmergencyPrediction({
    required this.label,
    required this.confidence,
    required this.isEmergency,
    required this.probabilities,
  });

  final String label;
  final double confidence;
  final bool isEmergency;
  final Map<String, double> probabilities;

  factory EmergencyPrediction.fromJson(Map<String, dynamic> json) {
    final probabilities = <String, double>{};
    final rawProbabilities = json['probabilities'];
    if (rawProbabilities is Map) {
      rawProbabilities.forEach((key, value) {
        probabilities[key.toString()] = (value as num?)?.toDouble() ?? 0.0;
      });
    }

    return EmergencyPrediction(
      label: json['label']?.toString() ?? 'Unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      isEmergency: json['is_emergency'] as bool? ?? false,
      probabilities: probabilities,
    );
  }
}

class EmergencyBackendService {
  const EmergencyBackendService();

  Future<bool> checkHealth() async {
    final response = await http.get(Uri.parse(BackendEndpoints.emergencyHealth));
    debugPrint('Emergency backend health status: ${response.statusCode}');
    return response.statusCode == 200;
  }

  Future<EmergencyPrediction> predictFromBytes(Uint8List imageBytes) async {
    final request = http.MultipartRequest('POST', Uri.parse(BackendEndpoints.emergencyPredict));
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        imageBytes,
        filename: 'emergency.jpg',
        contentType: MediaType('image', 'jpeg'),
      ),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    debugPrint('Emergency backend predict response: ${response.statusCode}');
    if (response.statusCode != 200) {
      String errorMessage = 'Failed to predict emergency gesture';
      try {
        final errorBody = jsonDecode(response.body) as Map<String, dynamic>;
        errorMessage = errorBody['detail']?.toString() ?? errorMessage;
      } catch (_) {
        errorMessage = response.body;
      }
      throw Exception(errorMessage);
    }

    return EmergencyPrediction.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
