import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

class FeatureHubScreen extends StatelessWidget {
  const FeatureHubScreen({super.key, required this.availableCameras});

  final List<CameraDescription> availableCameras;

  @override
  Widget build(BuildContext context) {
    final items = <_FeatureItem>[
      _FeatureItem(
        title: 'Sign Language',
        subtitle: 'Live hand sign detection and avatar output',
        icon: Icons.gesture,
        route: '/sign',
        color: const Color(0xFF06B6D4),
      ),
      _FeatureItem(
        title: 'Speech',
        subtitle: 'Text to speech and speech to text',
        icon: Icons.record_voice_over,
        route: '/speech',
        color: const Color(0xFF22C55E),
      ),
      _FeatureItem(
        title: 'Emergency AI',
        subtitle: 'Hand gesture emergency detection',
        icon: Icons.warning_amber_rounded,
        route: '/emergency',
        color: const Color(0xFFEF4444),
      ),
      _FeatureItem(
        title: 'Prescription Safety',
        subtitle: 'OCR, allergy, and interaction checks',
        icon: Icons.medical_services,
        route: '/prescription',
        color: const Color(0xFFF59E0B),
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('MediSign Features'),
        backgroundColor: const Color(0xFF111827),
      ),
      backgroundColor: const Color(0xFF0B1220),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Choose a module',
            style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Each feature opens in its own screen and talks to its own backend service.',
            style: TextStyle(color: Colors.white70),
          ),
          const SizedBox(height: 20),
          ...items.map(
            (item) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () => Navigator.of(context).pushNamed(item.route),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF111827),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: item.color.withOpacity(0.4)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 52,
                        height: 52,
                        decoration: BoxDecoration(
                          color: item.color.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Icon(item.icon, color: item.color),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(item.title, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 4),
                            Text(item.subtitle, style: const TextStyle(color: Colors.white70)),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right, color: Colors.white54),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FeatureItem {
  const _FeatureItem({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.route,
    required this.color,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final String route;
  final Color color;
}
