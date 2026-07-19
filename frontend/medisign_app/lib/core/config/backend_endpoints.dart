class BackendEndpoints {
  const BackendEndpoints._();

  static const signPrediction = 'http://127.0.0.1:5000/predict';
  static const avatarParse = 'http://127.0.0.1:5000/api/v1/avatar/parse';
  static const ttsVoices = 'http://127.0.0.1:5001/api/v1/tts/voices';
  static const ttsSpeak = 'http://127.0.0.1:5001/api/v1/tts/speak';
  static const sttTranscribe = 'http://127.0.0.1:5000/api/v1/stt/transcribe';
}
