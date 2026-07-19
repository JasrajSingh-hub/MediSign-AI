import 'package:flutter/material.dart';

class AvatarPosePainter extends CustomPainter {
  const AvatarPosePainter({required this.joints});

  final Map<String, dynamic> joints;

  static const List<List<int>> _handConnections = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [0, 5],
    [5, 6],
    [6, 7],
    [7, 8],
    [0, 9],
    [9, 10],
    [10, 11],
    [11, 12],
    [0, 13],
    [13, 14],
    [14, 15],
    [15, 16],
    [0, 17],
    [17, 18],
    [18, 19],
    [19, 20],
  ];

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

    final leftHand = _pointsFromLandmarks(joints['left_hand'], size);
    final rightHand = _pointsFromLandmarks(joints['right_hand'], size);
    final hand = _pointsFromLandmarks(joints['hand'], size);
    if (leftHand.isNotEmpty || rightHand.isNotEmpty || hand.isNotEmpty) {
      _drawHand(canvas, leftHand, linePaint, jointPaint);
      _drawHand(canvas, rightHand, linePaint, jointPaint);
      _drawHand(canvas, hand, linePaint, jointPaint);
      return;
    }

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

  List<Offset> _pointsFromLandmarks(dynamic landmarks, Size size) {
    if (landmarks is! List || landmarks.isEmpty) {
      return const [];
    }

    final rawPoints = <({double x, double y})>[];
    for (final landmark in landmarks) {
      if (landmark is! Map) {
        continue;
      }

      final x = (landmark['x'] as num?)?.toDouble();
      final y = (landmark['y'] as num?)?.toDouble();
      if (x != null && y != null) {
        rawPoints.add((x: x, y: y));
      }
    }

    if (rawPoints.isEmpty) {
      return const [];
    }

    final minX = rawPoints.map((point) => point.x).reduce((a, b) => a < b ? a : b);
    final maxX = rawPoints.map((point) => point.x).reduce((a, b) => a > b ? a : b);
    final minY = rawPoints.map((point) => point.y).reduce((a, b) => a < b ? a : b);
    final maxY = rawPoints.map((point) => point.y).reduce((a, b) => a > b ? a : b);
    final rangeX = (maxX - minX).abs() < 0.001 ? 1.0 : maxX - minX;
    final rangeY = (maxY - minY).abs() < 0.001 ? 1.0 : maxY - minY;
    final scale = size.shortestSide * 0.72;
    final offset = Offset(
      (size.width - scale) / 2,
      (size.height - scale) / 2,
    );

    return rawPoints
        .map(
          (point) => Offset(
            offset.dx + ((point.x - minX) / rangeX) * scale,
            offset.dy + ((point.y - minY) / rangeY) * scale,
          ),
        )
        .toList();
  }

  void _drawHand(
    Canvas canvas,
    List<Offset> points,
    Paint linePaint,
    Paint jointPaint,
  ) {
    if (points.isEmpty) {
      return;
    }

    for (final connection in _handConnections) {
      final start = connection[0];
      final end = connection[1];
      if (start < points.length && end < points.length) {
        canvas.drawLine(points[start], points[end], linePaint);
      }
    }

    for (final point in points) {
      canvas.drawCircle(point, 4, jointPaint);
    }
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
