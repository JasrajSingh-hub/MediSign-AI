import 'dart:io';

class BackendEndpoints {
  const BackendEndpoints._();

  static const signPrediction = 'http://127.0.0.1:5000/predict';
  static const avatarParse = 'http://127.0.0.1:5000/api/v1/avatar/parse';
  static const ttsVoices = 'http://127.0.0.1:5000/api/v1/tts/voices';
  static const ttsSpeak = 'http://127.0.0.1:5000/api/v1/tts/speak';
  static const sttTranscribe = 'http://127.0.0.1:5000/api/v1/stt/transcribe';
  static const emergencyHealth = 'http://127.0.0.1:5000/api/v1/emergency/health';
  static const emergencyStatus = 'http://127.0.0.1:5000/api/v1/emergency/status';
  static const emergencyPredict = 'http://127.0.0.1:5000/api/v1/emergency/predict';
  static const moduleBHealth = 'http://127.0.0.1:5000/health';
  static const moduleBOcrAudit = 'http://127.0.0.1:5000/api/v1/prescription/ocr-audit';
}
