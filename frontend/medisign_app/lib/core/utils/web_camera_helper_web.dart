import 'dart:html' as html;

Future<void> requestWebCameraPermissionImpl() async {
  try {
    await html.window.navigator.mediaDevices?.getUserMedia({'video': true});
  } catch (_) {}
}
