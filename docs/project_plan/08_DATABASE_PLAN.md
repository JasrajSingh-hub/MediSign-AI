# MediSign-AI: Local Data Persistence Design

This document details the local persistence layouts for user preferences and history caching within the Flutter client, prioritizing lightweight persistence for the MVP and deferring relational databases to Phase 2.

---

## 1. MVP Persistence Strategy (SharedPreferences)

To avoid the overhead of managing local database migrations during initial feature integration, the MVP will utilize `SharedPreferences` as its single persistence layer.

### A. Key-Value Settings Map
Configuration settings are mapped to direct preference keys:
* `pref_backend_url` (String, Default: `http://127.0.0.1:8000`)
* `pref_confidence_threshold` (Double, Default: `0.80`)
* `pref_enable_tts` (Boolean, Default: `true`)
* `pref_enable_alarm` (Boolean, Default: `true`)
* `pref_enable_vibration` (Boolean, Default: `true`)
* `pref_camera_fps` (Int, Default: `3`)
* `pref_theme_dark` (Boolean, Default: `true`)
* `pref_developer_mode` (Boolean, Default: `false`)

### B. Lightweight History Caching
Prediction histories and OCR records are stored as serialized JSON strings:
* **Key**: `cached_prediction_history`
* **Format**: List of serialized JSON objects.
* **Schema**:
  ```json
  [
    {
      "module_type": "emergency",
      "predicted_label": "help",
      "confidence": 0.942,
      "latency_ms": 154,
      "timestamp": "2026-07-17T16:10:00Z"
    }
  ]
  ```
* **Caching Policy**: On new prediction outputs, read the string, deserialize it into a list, prepend the new record, limit the length to **50** entries, and save it back to SharedPreferences.

---

## 2. Phase 2 Persistence Schema (Optional SQLite Integration)

If persistence requirements scale (e.g. detailed clinical records, search indexes, or audit logs), the application will migrate history and OCR storage to an SQLite database (`sqflite`).

### A. Schema: `prediction_history`
```sql
CREATE TABLE prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_type TEXT NOT NULL,
    predicted_label TEXT NOT NULL,
    confidence REAL NOT NULL,
    latency_ms INTEGER NOT NULL,
    timestamp TEXT NOT NULL
);
```

### B. Schema: `prescription_records`
```sql
CREATE TABLE prescription_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    doctor_name TEXT,
    hospital_name TEXT,
    raw_text TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```
