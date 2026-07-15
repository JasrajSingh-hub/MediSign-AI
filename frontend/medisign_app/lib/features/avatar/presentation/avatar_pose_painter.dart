import 'package:flutter/material.dart';

class AvatarPosePainter extends CustomPainter {
  const AvatarPosePainter({required this.joints});

  final Map<String, dynamic> joints;

  @override
  void paint(Canvas canvas, Size size) {
    final framePaint = Paint()
      ..color = joints.isEmpty
          ? Colors.white.withOpacity(0.05)
          : Colors.cyanAccent.withOpacity(0.08);

    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Offset.zero & size,
        const Radius.circular(12),
      ),
      framePaint,
    );

    if (joints.isEmpty) {
      return;
    }

    final linePaint = Paint()
      ..color = Colors.cyanAccent
      ..strokeWidth = 5
      ..strokeCap = StrokeCap.round;

    final jointPaint = Paint()..color = Colors.greenAccent;

    final head = _pointFromJoint(joints['head'], size);
    final leftShoulder = _pointFromJoint(joints['left_shoulder'], size);
    final rightShoulder = _pointFromJoint(joints['right_shoulder'], size);
    final leftElbow = _pointFromJoint(joints['left_elbow'], size);
    final rightElbow = _pointFromJoint(joints['right_elbow'], size);
    final leftWrist = _pointFromJoint(joints['left_wrist'], size);
    final rightWrist = _pointFromJoint(joints['right_wrist'], size);

    if (head != null) {
      canvas.drawCircle(head, 18, jointPaint);
    }

    _drawLimb(canvas, leftShoulder, rightShoulder, linePaint);
    _drawLimb(canvas, leftShoulder, leftElbow, linePaint);
    _drawLimb(canvas, leftElbow, leftWrist, linePaint);
    _drawLimb(canvas, rightShoulder, rightElbow, linePaint);
    _drawLimb(canvas, rightElbow, rightWrist, linePaint);

    for (final point in [
      leftShoulder,
      rightShoulder,
      leftElbow,
      rightElbow,
      leftWrist,
      rightWrist,
    ]) {
      if (point != null) {
        canvas.drawCircle(point, 8, jointPaint);
      }
    }
  }

  Offset? _pointFromJoint(dynamic joint, Size size) {
    if (joint is! Map) {
      return null;
    }

    final x = (joint['x'] as num?)?.toDouble();
    final y = (joint['y'] as num?)?.toDouble();
    if (x == null || y == null) {
      return null;
    }

    return Offset(x * size.width, y * size.height);
  }

  void _drawLimb(Canvas canvas, Offset? start, Offset? end, Paint paint) {
    if (start == null || end == null) {
      return;
    }
    canvas.drawLine(start, end, paint);
  }

  @override
  bool shouldRepaint(covariant AvatarPosePainter oldDelegate) {
    return oldDelegate.joints != joints;
  }
}
