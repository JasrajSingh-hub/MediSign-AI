# MediSign-AI: Settings Configuration Plan

This document details the configuration parameters, defaults, and validation constraints for the Settings module.

---

## 1. Parameters Specification

| Setting Name | Key | Type | Bounds / Options | Default Value | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Inference Threshold** | `pref_confidence_threshold` | Double | `0.50` - `1.00` | `0.80` | Must be a double value. |
| **TTS Alert Speech** | `pref_enable_tts` | Boolean | `true` / `false` | `true` | Must not be null. |
| **Audio Buzzer** | `pref_enable_alarm` | Boolean | `true` / `false` | `true` | Must not be null. |
| **Haptic Vibration** | `pref_enable_vibration` | Boolean | `true` / `false` | `true` | Must not be null. |
| **Prediction URL** | `pref_backend_url` | String | URL | `http://127.0.0.1:8000` | Must parse as a valid URI. |
| **Inference Interval** | `pref_prediction_interval` | Integer | `300` - `1000` ms | `300` | Minimum 300ms to avoid network overhead. |
| **Theme Selection** | `pref_theme_dark` | Boolean | `true` / `false` | `true` | Matches app styling. |
| **Developer Mode Toggle**| `pref_developer_mode` | Boolean | `true` / `false` | `false` | Unlocked by tapping header 7 times. |
| **Mock API Responses** | `pref_mock_api` | Boolean | `true` / `false` | `false` | Only visible in Developer Mode. |
| **Performance HUD** | `pref_perf_hud` | Boolean | `true` / `false` | `false` | Renders overlays on screen when true. |

---

## 2. Validation Constraints

* **API URL Check**: On editing the base URL, the settings provider runs an asynchronous validation check. It appends `/health` to the URI and sends a GET request. If the request succeeds within a 1.5-second timeout, the URL is saved; otherwise, the app displays a toast: `"Invalid backend server. Verification failed."`.
* **Confidence Range Rules**: Limits the confidence threshold slider between 0.50 and 1.00. Setting the value too low can lead to frequent false alarms.
* **Prediction Interval Safety**: If the user reduces the prediction interval below 300ms, alert them that high-frequency calls can increase CPU load and cause thermal issues on low-end devices.
