import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

class FeatureHubScreen extends StatelessWidget {
  const FeatureHubScreen({super.key, required this.availableCameras});

  final List<CameraDescription> availableCameras;

  @override
  Widget build(BuildContext context) {
    final features = <_FeatureCardData>[
      const _FeatureCardData(
        title: 'Sign AI',
        subtitle: 'Real-time ASL translation for patient intake and triage.',
        icon: Icons.sign_language,
        route: '/sign',
        accent: Color(0xFF68F5B8),
        status: 'Active Session',
        statusTone: _StatusTone.success,
      ),
      const _FeatureCardData(
        title: 'Rx Safety',
        subtitle: 'Automated contraindication and dosage verification.',
        icon: Icons.medical_services_outlined,
        route: '/prescription',
        accent: Color(0xFF22D3EE),
        status: 'System Ready',
        statusTone: _StatusTone.primary,
      ),
      const _FeatureCardData(
        title: 'Code Alert',
        subtitle: 'Predictive vitals monitoring and rapid response routing.',
        icon: Icons.emergency,
        route: '/emergency',
        accent: Color(0xFFEF4444),
        status: 'Monitoring',
        statusTone: _StatusTone.danger,
      ),
      const _FeatureCardData(
        title: 'Vocalizer',
        subtitle: 'Text-to-speech engine for non-verbal communication.',
        icon: Icons.spatial_audio,
        route: '/speech',
        accent: Color(0xFFB9C8DF),
        status: 'Standby',
        statusTone: _StatusTone.neutral,
      ),
    ];

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            _Header(onProfileTap: () {}),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                children: [
                  _HeroPanel(onSignTap: () => Navigator.of(context).pushNamed('/sign')),
                  const SizedBox(height: 16),
                  ...features.map(
                    (feature) => Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: _FeatureCard(
                        data: feature,
                        onTap: () => Navigator.of(context).pushNamed(feature.route),
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  _SystemLogCard(
                    onViewAll: () => Navigator.of(context).pushNamed('/sign'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
        bottomNavigationBar: NavigationBar(
        selectedIndex: 0,
        backgroundColor: const Color(0xFF122031).withOpacity(0.96),
        indicatorColor: const Color(0xFF22D3EE).withOpacity(0.16),
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.visibility_outlined), selectedIcon: Icon(Icons.visibility), label: 'Sign AI'),
          NavigationDestination(icon: Icon(Icons.medical_services_outlined), selectedIcon: Icon(Icons.medical_services), label: 'Safety'),
          NavigationDestination(icon: Icon(Icons.emergency_outlined), selectedIcon: Icon(Icons.emergency), label: 'Alert'),
        ],
        onDestinationSelected: (index) {
          if (index == 1) {
            Navigator.of(context).pushNamed('/sign');
          } else if (index == 2) {
            Navigator.of(context).pushNamed('/prescription');
          } else if (index == 3) {
            Navigator.of(context).pushNamed('/emergency');
          }
        },
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onProfileTap});

  final VoidCallback onProfileTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 72,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF122031).withOpacity(0.84),
        boxShadow: const [
          BoxShadow(color: Colors.black26, blurRadius: 16, offset: Offset(0, 6)),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFF1D2B3C),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white12),
            ),
            child: const Icon(Icons.local_hospital, color: Color(0xFF22D3EE), size: 22),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'MediSign',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFFD5E4FA)),
                ),
                SizedBox(height: 2),
                Text(
                  'Clinical operations dashboard',
                  style: TextStyle(fontSize: 12, color: Color(0xFFBBC9CD)),
                ),
              ],
            ),
          ),
          InkWell(
            onTap: onProfileTap,
            borderRadius: BorderRadius.circular(999),
            child: const CircleAvatar(
              radius: 18,
              backgroundColor: Color(0xFF283647),
              child: Icon(Icons.person, color: Color(0xFFD5E4FA), size: 20),
            ),
          ),
        ],
      ),
    );
  }
}

class _HeroPanel extends StatelessWidget {
  const _HeroPanel({required this.onSignTap});

  final VoidCallback onSignTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF122031), Color(0xFF0E1C2D)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: Colors.white10),
        boxShadow: const [
          BoxShadow(color: Colors.black26, blurRadius: 24, offset: Offset(0, 10)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Clinical Operations',
            style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700, color: Color(0xFFD5E4FA)),
          ),
          const SizedBox(height: 10),
          const Text(
            'System nominal. All AI modules are online and monitoring.',
            style: TextStyle(fontSize: 14, height: 1.4, color: Color(0xFFBBC9CD)),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _StatusPill(
                label: '4 modules online',
                tone: _StatusTone.success,
                icon: Icons.check_circle,
              ),
              const SizedBox(width: 10),
              _StatusPill(
                label: 'Live patient support',
                tone: _StatusTone.primary,
                icon: Icons.monitor_heart,
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: onSignTap,
              icon: const Icon(Icons.play_arrow),
              label: const Text('Open Sign AI'),
            ),
          ),
        ],
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  const _FeatureCard({required this.data, required this.onTap});

  final _FeatureCardData data;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF122031).withOpacity(0.92),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: data.accent.withOpacity(0.2)),
            boxShadow: const [
              BoxShadow(color: Colors.black26, blurRadius: 18, offset: Offset(0, 8)),
            ],
          ),
          child: Column(
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: data.accent.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Icon(data.icon, color: data.accent, size: 26),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          data.title,
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFFD5E4FA)),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          data.subtitle,
                          style: const TextStyle(fontSize: 13, height: 1.35, color: Color(0xFFBBC9CD)),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.arrow_forward, color: data.accent.withOpacity(0.8)),
                ],
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  _StatusPill(label: data.status, tone: data.statusTone, icon: Icons.circle, compact: true),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SystemLogCard extends StatelessWidget {
  const _SystemLogCard({required this.onViewAll});

  final VoidCallback onViewAll;

  @override
  Widget build(BuildContext context) {
    final logItems = const <_LogItem>[
      _LogItem(
        title: 'ASL Session Completed',
        subtitle: 'Triage Rm 4 • 2 mins ago',
        icon: Icons.done_all,
        tone: _StatusTone.success,
      ),
      _LogItem(
        title: 'Rx Verification Passed',
        subtitle: 'Dr. Chen • 15 mins ago',
        icon: Icons.verified,
        tone: _StatusTone.primary,
      ),
      _LogItem(
        title: 'Elevated HR Detected',
        subtitle: 'Bed 12 • 45 mins ago',
        icon: Icons.warning,
        tone: _StatusTone.danger,
      ),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'System Log',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFFD5E4FA)),
            ),
            TextButton(onPressed: onViewAll, child: const Text('View All')),
          ],
        ),
        const SizedBox(height: 8),
        ...logItems.map(
          (item) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF0E1C2D),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.white10),
              ),
              child: Row(
                children: [
                  Container(
                    width: 38,
                    height: 38,
                    decoration: BoxDecoration(
                      color: item.tone.color.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(item.icon, color: item.tone.color, size: 18),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.title,
                          style: const TextStyle(color: Color(0xFFD5E4FA), fontSize: 13, fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          item.subtitle,
                          style: const TextStyle(color: Color(0xFFBBC9CD), fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({
    required this.label,
    required this.tone,
    required this.icon,
    this.compact = false,
  });

  final String label;
  final _StatusTone tone;
  final IconData icon;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: compact ? 9 : 11, vertical: compact ? 6 : 8),
      decoration: BoxDecoration(
        color: tone.color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: tone.color.withOpacity(0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon == Icons.circle)
            Container(width: 8, height: 8, decoration: BoxDecoration(color: tone.color, shape: BoxShape.circle))
          else
            Icon(icon, size: 14, color: tone.color),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(color: tone.color, fontSize: compact ? 11 : 12, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}

class _FeatureCardData {
  const _FeatureCardData({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.route,
    required this.accent,
    required this.status,
    required this.statusTone,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final String route;
  final Color accent;
  final String status;
  final _StatusTone statusTone;
}

class _LogItem {
  const _LogItem({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.tone,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final _StatusTone tone;
}

enum _StatusTone { success, primary, danger, neutral }

extension on _StatusTone {
  Color get color {
    switch (this) {
      case _StatusTone.success:
        return const Color(0xFF68F5B8);
      case _StatusTone.primary:
        return const Color(0xFF22D3EE);
      case _StatusTone.danger:
        return const Color(0xFFEF4444);
      case _StatusTone.neutral:
        return const Color(0xFFB9C8DF);
    }
  }
}
