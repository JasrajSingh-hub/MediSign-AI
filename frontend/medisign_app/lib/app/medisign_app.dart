import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../features/dashboard/presentation/medisign_dashboard_screen.dart';
import 'app_theme.dart';

class MediSignApp extends StatelessWidget {
  const MediSignApp({super.key, required this.availableCameras});

  final List<CameraDescription> availableCameras;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: buildMediSignTheme(),
      home: MediSignDashboardScreen(availableCameras: availableCameras),
    );
  }
}
