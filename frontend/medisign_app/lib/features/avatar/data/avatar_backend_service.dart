import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

import '../../../core/config/backend_endpoints.dart';

class AvatarBackendService {
  const AvatarBackendService();
Future<Map<String, dynamic>> loadCoordinateLibrary() async {
  final jsonString = await rootBundle.loadString('assets/avatar_library.json');
  return jsonDecode(jsonString) as Map<String, dynamic>;
}

  Future<List<String>> parseTokens(String text) async {
    final response = await http.post(
      Uri.parse(BackendEndpoints.avatarParse),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text}),
    );

    if (response.statusCode != 200) {
      throw Exception('Avatar parse failed (${response.statusCode})');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return List<String>.from(data['tokens'] ?? const []);
  }
}
