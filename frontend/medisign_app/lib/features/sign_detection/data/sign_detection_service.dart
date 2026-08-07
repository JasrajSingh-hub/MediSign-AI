import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/config/backend_endpoints.dart';

class SignPrediction {
  const SignPrediction({
    required this.letter,
    required this.confidence,
  });

  final String letter;
  final String confidence;

  String get displayText => 'Detected Sign: $letter ($confidence)';
}

class SignDetectionService {
  const SignDetectionService();

  Future<SignPrediction?> predictFromImageBytes(List<int> imageBytes) async {
    final response = await http
        .post(
          Uri.parse(BackendEndpoints.signPrediction),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'image': 'data:image/jpeg;base64,${base64Encode(imageBytes)}',
          }),
        )
        .timeout(const Duration(milliseconds: 400));

    if (response.statusCode != 200) {
      return null;
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return SignPrediction(
      letter: data['letter']?.toString() ?? '',
      confidence: data['confidence']?.toString() ?? '',
    );
  }
}
