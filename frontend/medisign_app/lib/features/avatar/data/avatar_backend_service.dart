import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

import '../../../core/config/backend_endpoints.dart';

class AvatarBackendService {
  const AvatarBackendService();

  Future<Map<String, dynamic>> loadCoordinateLibrary() async {
    final jsonString = await rootBundle.loadString('assets/avatar_library.json');
    final decoded = jsonDecode(jsonString);
    if (decoded is Map) {
      return Map<String, dynamic>.from(decoded);
    }
    throw Exception('Avatar library must be a JSON object');
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

    final decoded = jsonDecode(response.body);
    if (decoded is List) {
      if (decoded.isNotEmpty && decoded.first is Map) {
        final tokens = (decoded.first as Map)['tokens'];
        if (tokens is List) {
          return tokens.map((token) => token.toString()).toList();
        }
      }
      return decoded.map((token) => token.toString()).toList();
    }

    if (decoded is Map) {
      final tokens = decoded['tokens'];
      if (tokens is List) {
        return tokens.map((token) => token.toString()).toList();
      }
    }

    throw Exception('Avatar parse returned an invalid response');
  }
}
