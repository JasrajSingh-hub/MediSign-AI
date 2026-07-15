# Frontend Code Map

## App Shell
- `main.dart`: boots Flutter and collects device cameras.
- `app/`: app-level wiring such as theme and root widget.

## Features
- `features/dashboard/presentation/`: main screen that composes all features.
- `features/sign_detection/data/`: camera frame prediction API code.
- `features/speech/data/`: voice loading, text-to-speech, and speech-to-text API code.
- `features/avatar/data/`: avatar library loading and token parsing API code.
- `features/avatar/presentation/`: avatar rendering code.

## Shared Config
- `core/config/`: backend URLs and cross-feature config values.
