import 'dart:ui';

import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../../core/config/backend_endpoints.dart';

class SignPrediction {
  const SignPrediction({
    required this.letter,
    required this.confidence,
    required this.letterConfirmed,
    required this.currentWord,
    required this.handLandmarks,
  });

  final String letter;
  final String confidence;
  final bool letterConfirmed;
  final String currentWord;
  final List<List<Offset>> handLandmarks;

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
      letterConfirmed: data['letter_confirmed'] == true,
      currentWord: data['current_word']?.toString() ?? '',
      handLandmarks: _parseLandmarks(data['landmarks']),
    );
  }

  List<List<Offset>> _parseLandmarks(dynamic value) {
    if (value is! List) {
      return const [];
    }

    return value
        .whereType<List>()
        .map(
          (hand) => hand
              .whereType<Map>()
              .map((landmark) {
                final x = (landmark['x'] as num?)?.toDouble();
                final y = (landmark['y'] as num?)?.toDouble();
                if (x == null || y == null) {
                  return null;
                }
                return Offset(x, y);
              })
              .whereType<Offset>()
              .toList(),
        )
        .where((hand) => hand.isNotEmpty)
        .toList();
  }
}
