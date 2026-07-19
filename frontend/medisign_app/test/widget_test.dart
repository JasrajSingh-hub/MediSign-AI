import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medisign_app/main.dart';

void main() {
  testWidgets('Smoke test for MediSign-AI sandbox main navigation shell', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MediSignSandbox());

    // Verify that the bottom navigation bar is present
    expect(find.byType(BottomNavigationBar), findsOneWidget);
    
    // Verify that the first tab "Sign Language" is selected and rendered
    expect(find.text('Sign Language'), findsOneWidget);
    expect(find.text('MEDI-SIGN AI TRANSLATION OUTPUT:'), findsOneWidget);
  });
}
