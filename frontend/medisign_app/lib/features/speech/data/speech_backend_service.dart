import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../../../core/config/backend_endpoints.dart';

class VoiceOption {
  const VoiceOption({
    required this.name,
    required this.locale,
    required this.gender,
  });

  final String name;
  final String locale;
  final String gender;

  factory VoiceOption.fromJson(Map<String, dynamic> json) {
    return VoiceOption(
      name: json['name']?.toString() ?? '',
      locale: json['locale']?.toString() ?? 'en-US',
      gender: json['gender']?.toString() ?? 'unknown',
    );
  }

  String get shortName {
    final segments = name.split('-');
    return segments.isEmpty ? name : segments.last;
  }

  String get genderSymbol =>
      gender.toLowerCase() == 'female' ? 'F' : 'M';
}

class SpeechBackendService {
  const SpeechBackendService();

  Future<List<VoiceOption>> fetchVoices() async {
    final response = await http.get(Uri.parse(BackendEndpoints.ttsVoices));
    if (response.statusCode != 200) {
      throw Exception('Failed to fetch voices');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final voiceList = List<dynamic>.from(data['voices'] ?? const []);

    return voiceList
        .map((voice) => VoiceOption.fromJson(Map<String, dynamic>.from(voice)))
        .toList();
  }

  String resolvePreferredVoiceName(List<VoiceOption> voices) {
    if (voices.isEmpty) {
      return '';
    }

    final preferredVoice = voices.firstWhere(
      (voice) =>
          voice.locale.toLowerCase().contains('in') ||
          voice.locale.toLowerCase().contains('us'),
      orElse: () => voices.first,
    );

    return preferredVoice.name;
  }

  String resolveLanguage({
    required List<VoiceOption> voices,
    required String? selectedVoiceName,
  }) {
    if (selectedVoiceName == null || selectedVoiceName.isEmpty) {
      return 'en-US';
    }

    final matchingVoice = voices.where((voice) => voice.name == selectedVoiceName);
    if (matchingVoice.isEmpty) {
      return 'en-US';
    }

    return matchingVoice.first.locale;
  }

  Future<Uint8List> synthesizeSpeech({
    required String text,
    required String language,
  }) async {
    final response = await http.post(
      Uri.parse(BackendEndpoints.ttsSpeak),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
        'language': language,
        'session_id': 'flutter-session-${DateTime.now().millisecondsSinceEpoch}',
      }),
    );

    if (response.statusCode != 200) {
      String errorMessage = 'Failed to synthesize speech';
      try {
        final errorBody = jsonDecode(response.body) as Map<String, dynamic>;
        errorMessage = errorBody['detail']?.toString() ?? errorMessage;
      } catch (_) {
        errorMessage = response.body;
      }
      throw Exception(errorMessage);
    }

    return response.bodyBytes;
  }

  Future<String> transcribeAudio({
    required Uint8List audioBytes,
    required String language,
  }) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse(BackendEndpoints.sttTranscribe),
    );

    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        audioBytes,
        filename: 'audio.wav',
        contentType: MediaType('audio', 'wav'),
      ),
    );
    request.fields['language'] = language;

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      String errorMessage = 'Failed to transcribe speech';
      try {
        final errorBody = jsonDecode(response.body) as Map<String, dynamic>;
        errorMessage = errorBody['detail']?.toString() ?? errorMessage;
      } catch (_) {
        errorMessage = response.body;
      }
      throw Exception(errorMessage);
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return data['text']?.toString() ?? '';
  }
}
