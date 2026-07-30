import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../features/dashboard/presentation/medisign_dashboard_screen.dart';
import '../features/emergency/presentation/emergency_screen.dart';
import '../features/hub/presentation/feature_hub_screen.dart';
import '../features/prescription/presentation/prescription_screen.dart';
import '../features/speech/presentation/speech_screen.dart';
import 'app_theme.dart';

class MediSignApp extends StatelessWidget {
  const MediSignApp({super.key, required this.availableCameras});

  final List<CameraDescription> availableCameras;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: buildMediSignTheme(),
      home: FeatureHubScreen(availableCameras: availableCameras),
      routes: {
        '/sign': (_) => MediSignDashboardScreen(availableCameras: availableCameras),
        '/speech': (_) => const SpeechScreen(),
        '/emergency': (_) => EmergencyScreen(availableCameras: availableCameras),
        '/prescription': (_) => const PrescriptionScreen(),
      },
    );
  }
}
