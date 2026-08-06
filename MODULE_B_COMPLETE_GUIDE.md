# Module B — Complete Technical Guide & Usage Manual
## Prescription OCR, Allergy Detection, Drug Interaction Audit & Flutter Integration

> **Module B Scope**: Offline-first, low-latency Prescription Safety Subsystem for MediSign AI. Handles handwritten & printed prescription OCR, brand-to-generic resolution, allergy set-intersection auditing, 4-level drug interaction detection, and safe alternative drug recommendations.

---

## 📑 Table of Contents
1. [System Overview & Architecture](#1-system-overview--architecture)
2. [Prescription OCR Subsystem](#2-prescription-ocr-subsystem)
   - [Tier 1: Cloud Vision OCR (`vision_ocr_service.py`)](#tier-1-cloud-vision-ocr-vision_ocr_servicepy)
   - [Tier 2: On-Device Neural Handwriting OCR (`trocr_service.py`)](#tier-2-on-device-neural-handwriting-ocr-trocr_servicepy)
   - [Tier 3: Local Tesseract Printed OCR (`ocr_service.py`)](#tier-3-local-tesseract-printed-ocr-ocr_servicepy)
   - [Fuzzy Drug Matcher & Brand Resolution (`drug_matcher.py`)](#fuzzy-drug-matcher--brand-resolution-drug_matcherpy)
3. [Allergy Detection Engine](#3-allergy-detection-engine)
4. [Drug Interaction Checker](#4-drug-interaction-checker)
5. [Alternative Drug Recommendation Engine](#5-alternative-drug-recommendation-engine)
6. [API Endpoints Reference](#6-api-endpoints-reference)
7. [Step-by-Step: How to Run, Test, and Verify](#7-step-by-step-how-to-run-test-and-verify)
   - [Backend Installation & Environment Setup](#backend-installation--environment-setup)
   - [Starting the FastAPI Server](#starting-the-fastapi-server)
   - [Running the Automated Test Suite](#running-the-automated-test-suite)
   - [Testing Custom Prescription Images](#testing-custom-prescription-images)
   - [Running the Flutter Test UI on Chrome](#running-the-flutter-test-ui-on-chrome)

---

## 1. System Overview & Architecture

Module B is designed with a **Feature-First Clean Architecture + MVVM** pattern. The FastAPI backend exposes RESTful endpoints for the Flutter client app (`MediSign App`).

```text
[ Prescription Image / Camera ]
               │
               ▼
   [ 3-Tier Multi-Engine OCR ] ──► Extracts Drug Names, Brands, Dosages
               │
               ▼
  [ Brand-to-Generic Resolver ] ──► Converts "Augmentin" -> "amoxicillin"
               │
               ▼
     [ Merged Audit Engine ]
      ├── Allergy Checker (Set Intersection vs Patient Allergy Profile)
      ├── Drug Interaction Matrix (C(n,2) Pairwise Check, 4 Severity Tiers)
      └── Alternative Drug Recommender (Suggests Non-Conflicting Class)
               │
               ▼
 [ Unified JSON / Flutter Web UI ]
```

---

## 2. Prescription OCR Subsystem

### Tier 1: Cloud Vision OCR (`vision_ocr_service.py`)
- **Primary Path**: High-accuracy multimodal LLM parsing via Gemini 1.5/2.5 Flash (`GEMINI_API_KEY`) or OpenRouter (`OPENROUTER_API_KEY`).
- **Functionality**: Accepts prescription images (PNG/JPEG) and directly returns structured JSON containing:
  ```json
  {
    "drugs": [
      {
        "name": "amoxicillin",
        "brand": "Augmentin 625",
        "dosage": "625mg",
        "frequency": "twice daily"
      }
    ]
  }
  ```
- **Robust Parsing**: Includes automatic fallback regex matchers (`r"\{[\s\S]*\}"`) to safely parse raw conversational outputs or markdown code blocks into JSON.

### Tier 2: On-Device Neural Handwriting OCR (`trocr_service.py`)
- **Secondary Offline Path**: On-device neural OCR powered by Microsoft TrOCR (`microsoft/trocr-small-handwritten`) via PyTorch and HuggingFace Transformers.
- **Functionality**: Runs completely locally on CPU/GPU when offline, extracting handwritten doctor notes without external network calls.

### Tier 3: Local Tesseract Printed OCR (`ocr_service.py`)
- **Tertiary Offline Path**: Tesseract OCR configured with `--psm 6 --oem 3 -l eng`.
- **Image Preprocessing**: Pillow + OpenCV pipeline (grayscale conversion, 2x upscaling, Otsu binarization, median denoising).

### Fuzzy Drug Matcher & Brand Resolution (`drug_matcher.py`)
- **RapidFuzz Engine**: Token-set ratio matching against generic ingredients and 299+ curated Indian brand names (`data/brand_names.csv`).
- **Brand Resolution Examples**:
  - `Augmentin` ➔ `amoxicillin`
  - `Dolo 650` / `PCM` ➔ `acetaminophen`
  - `Ecosprin` ➔ `aspirin`

---

## 3. Allergy Detection Engine

- **File**: `app/modules/prescription/services/allergy_checker.py`
- **Logic**: Class-level set-intersection check. Patients are typically allergic to drug *classes* (e.g., Penicillins) rather than individual drug names.
- **Algorithm**:
  1. Map prescribed drug ingredient ➔ RXCUI ➔ Allergy Class (using `data/drug_allergy_classes.csv` SQLite cache).
  2. Compare candidate classes against patient's allergy profile matrix.
  3. Flag matching allergy conflicts and provide severity details.

---

## 4. Drug Interaction Checker

- **File**: `app/modules/prescription/services/interaction_checker.py`
- **Logic**: Evaluates all $C(n, 2)$ unique pairwise combinations for $N$ prescribed drugs.
- **Severity Levels**:
  - `CONTRAINDICATED` (Deep Red) — High risk of life-threatening complications.
  - `MAJOR` (Red) — Significant clinical conflict; requires alternative or close monitoring.
  - `MODERATE` (Amber) — Potential interaction; adjust dosage or timing.
  - `MINOR` (Blue) — Slight interaction; minimal clinical impact.
- **Database**: 110 curated interaction pairs (`data/drug_interactions.csv`).

---

## 5. Alternative Drug Recommendation Engine

- **File**: `app/modules/prescription/services/allergy_checker.py` & `scripts/load_drug_alternatives.py`
- **Logic**: When an allergy conflict is detected, the engine queries `drug_alternatives.csv` to suggest alternative medications for the same condition, verifying that the patient is NOT allergic to the alternative drug class.

---

## 6. API Endpoints Reference

### 1. `POST /prescription/allergy-check`
- **Payload**:
  ```json
  {
    "patient_id": "P001",
    "drugs": ["amoxicillin", "ibuprofen"]
  }
  ```

### 2. `POST /prescription/interaction-check`
- **Payload**:
  ```json
  {
    "drugs": ["aspirin", "warfarin"]
  }
  ```

### 3. `POST /prescription/audit` (Merged Endpoint)
- Runs both Allergy Check and Interaction Check in a single call.

### 4. `POST /prescription/ocr-audit` (Multipart Upload)
- **Form Data**: `file` (image binary), `patient_id` (string).
- **Process**: Runs 3-tier OCR ➔ Drug Matcher ➔ Merged Audit ➔ Returns JSON with extracted drugs, raw OCR text, confidence scores, allergy alerts, alternatives, and interaction matrix.

---

## 7. Step-by-Step: How to Run, Test, and Verify

### Backend Installation & Environment Setup

1. **Navigate to the Backend Directory**:
   ```bash
   cd "c:/Users/karan yadav/Desktop/proj/MediSign-AI/module_b_backend"
   ```

2. **Verify Environment Variables (`.env`)**:
   Ensure `.env` contains your API key:
   ```env
   GEMINI_API_KEY=AQ.Ab8RN6KAPiVyBQOTsisEylrZbsZd_b3Z8Fq5l9gOA-pnkhw6Pw
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

---

### Starting the FastAPI Server

Run the development server using uvicorn:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs (Swagger UI): `http://127.0.0.1:8000/docs`

---

### Running the Automated Test Suite

Execute the full pytest suite (16 tests covering allergy, interaction, audit, and OCR):
```bash
python -m pytest tests/ -v
```

---

### Testing Custom Prescription Images

To test OCR extraction on any prescription image file:

```bash
python scripts/test_user_image.py
```
Or run the demo image verification script:
```bash
python scripts/verify_demo_images.py
```

---

### Running the Flutter Test UI on Chrome

To run the interactive web interface on Google Chrome:

```bash
cd "c:/Users/karan yadav/Desktop/proj/MediSign-AI modB/test_ui"
flutter run -d chrome
```

This launches a Flutter Web application where you can:
- Upload prescription camera scans or gallery photos.
- Inspect real-time OCR extraction results.
- View severity-colored allergy alerts and drug-drug interactions.
