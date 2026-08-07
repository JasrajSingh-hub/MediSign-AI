import 'dart:convert';
import 'dart:typed_data';
import 'dart:math';

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

class NearbyHospital {
  const NearbyHospital({
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.distanceMeters,
  });

  final String name;
  final double latitude;
  final double longitude;
  final double distanceMeters;
}

class EmergencyBackendService {
  const EmergencyBackendService();

  static const List<String> _overpassEndpoints = <String>[
    'https://overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
    'https://lz4.overpass-api.de/api/interpreter',
  ];

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

  Future<List<NearbyHospital>> fetchNearbyHospitals({
    required double latitude,
    required double longitude,
    int radiusMeters = 10000,
  }) async {
    final overpassQuery = '''
[out:json][timeout:30];
(nwr[amenity=hospital](around:$radiusMeters,$latitude,$longitude););
out center tags;
''';

    http.Response? response;
    for (final endpoint in _overpassEndpoints) {
      try {
        final candidateResponse = await http
            .post(
              Uri.parse(endpoint),
              headers: {'Content-Type': 'application/x-www-form-urlencoded'},
              body: {'data': overpassQuery},
            )
            .timeout(const Duration(seconds: 30));

        if (candidateResponse.statusCode == 200) {
          response = candidateResponse;
          break;
        }
      } catch (error) {
        debugPrint('Overpass lookup failed for $endpoint: $error');
      }
    }

    if (response == null) {
      return <NearbyHospital>[];
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final elements = List<dynamic>.from(data['elements'] ?? const []);
    final hospitals = <NearbyHospital>[];

    for (final element in elements) {
      final item = Map<String, dynamic>.from(element as Map);
      final tags = Map<String, dynamic>.from(item['tags'] as Map? ?? {});
      final name = tags['name']?.toString() ?? 'Unnamed hospital';
      final addressParts = <String>[
        tags['addr:housenumber']?.toString() ?? '',
        tags['addr:street']?.toString() ?? '',
        tags['addr:city']?.toString() ?? '',
      ].where((part) => part.trim().isNotEmpty).toList();
      final coordinates = _extractCoordinates(item);
      final lat = coordinates.$1;
      final lon = coordinates.$2;

      if (lat == 0.0 && lon == 0.0) {
        continue;
      }

      hospitals.add(
        NearbyHospital(
          name: addressParts.isEmpty ? name : '$name — ${addressParts.join(' ')}',
          latitude: lat,
          longitude: lon,
          distanceMeters: _distanceMeters(latitude, longitude, lat, lon),
        ),
      );
    }

    hospitals.sort((left, right) => left.distanceMeters.compareTo(right.distanceMeters));
    return hospitals;
  }

  double _distanceMeters(double lat1, double lon1, double lat2, double lon2) {
    const earthRadius = 6371000.0;
    final dLat = _degreesToRadians(lat2 - lat1);
    final dLon = _degreesToRadians(lon2 - lon1);
    final a =
        sin(dLat / 2) * sin(dLat / 2) +
            cos(_degreesToRadians(lat1)) * cos(_degreesToRadians(lat2)) *
                sin(dLon / 2) * sin(dLon / 2);
    final c = 2 * atan2(sqrt(a), sqrt(1 - a));
    return earthRadius * c;
  }

  double _degreesToRadians(double degrees) => degrees * (3.141592653589793 / 180.0);

  (double, double) _extractCoordinates(Map<String, dynamic> item) {
    final latValue = item['lat'];
    final lonValue = item['lon'];
    if (latValue is num && lonValue is num) {
      return (latValue.toDouble(), lonValue.toDouble());
    }

    final center = item['center'];
    if (center is Map) {
      final centerMap = Map<String, dynamic>.from(center);
      final centerLat = centerMap['lat'];
      final centerLon = centerMap['lon'];
      if (centerLat is num && centerLon is num) {
        return (centerLat.toDouble(), centerLon.toDouble());
      }
    }

    return (0.0, 0.0);
  }
}
