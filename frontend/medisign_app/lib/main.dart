import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import 'app/medisign_app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  List<CameraDescription> cameras = const [];
  try {
    cameras = await availableCameras();
  } catch (error) {
    debugPrint('Error finding cameras: $error');
  }

  runApp(MediSignApp(availableCameras: cameras));
}
