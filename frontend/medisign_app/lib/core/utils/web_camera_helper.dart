import 'web_camera_helper_stub.dart'
    if (dart.library.html) 'web_camera_helper_web.dart';

Future<void> requestWebCameraPermission() => requestWebCameraPermissionImpl();
