# Module B — Prescription OCR: Handwriting Support Plan

> Context document for LLM sessions working on the OCR sub-feature of Module B.
> Paste this alongside MODULE_B_CONTEXT.md and MODULE_B_FEATURE_INTENT.md at the
> start of any session where handwriting OCR is being discussed or built.

Last updated: 2026-08-04
Status: COMPLETE — Vision LLM (`vision_ocr_service.py`) & local TrOCR fallback (`trocr_service.py`) implemented and passing tests.

---

## 1. The Problem

### What we have now
Tesseract-based OCR that works on **printed/typed prescriptions only**.
Pipeline: image → preprocess (grayscale, binarize, denoise) → Tesseract (`-l eng`) →
raw text → drug_matcher (brand resolution + RapidFuzz fuzzy match) → drug name list.

Known limitations discovered in testing:
- Tesseract fails on handwritten text — architecturally wrong tool for the job.
- Mixed-language prescriptions (Bengali + English) pollute OCR output with garbage tokens.
  Partially fixed by `-l eng` config and ASCII-dominant line filter in drug_matcher.
- Brand names not recognized until brand_names table is seeded (95+ mappings added).
- Most real-world prescriptions from Indian doctors are **handwritten**, not printed.

### Why this matters
The entire Module B pipeline depends on OCR as its entry point. If OCR can't read
handwritten prescriptions, the allergy checker and interaction checker never get
invoked on the majority of real prescriptions a clinician would scan.

---

## 2. Why Tesseract Cannot Solve Handwriting

Tesseract was designed for printed text with consistent fonts. It has no mechanism
to handle:
- Variable letter shapes across different doctors' handwriting
- Inconsistent character spacing and slant
- Overlapping or connected letters (cursive)
- Abbreviated drug names (e.g., "Amox" for amoxicillin, "PCM" for paracetamol)
- Mixed scripts (Bengali instructions + English drug names on same page)

This is not a confidence threshold issue — Tesseract is the wrong architecture.
Training Tesseract on new data does not significantly improve handwriting accuracy.

---

## 3. Three Possible Approaches

### Approach A — Vision LLM API (RECOMMENDED for MVP)

**What it is:** Send the prescription image directly to a multimodal AI model
(GPT-4o, Gemini Vision, Claude) with a structured prompt asking it to extract
drug names and dosages. The model handles handwriting, abbreviations, mixed
languages, and brand names natively.

**How it works in the pipeline:**
```
[prescription image]
        |
        v
[Vision LLM API call]
  prompt: "Extract all drug names, dosages, and frequencies from this
           prescription image. Return JSON:
           {drugs: [{name, dosage, frequency}]}"
        |
        v
[structured JSON response]
  → drug names go into drug_matcher for brand resolution + RXCUI lookup
  → then allergy checker + interaction checker as normal
```

**Tech stack:**
- OpenAI GPT-4o Vision: `openai` Python SDK, `gpt-4o` model with image input
- Google Gemini Vision: `google-generativeai` SDK, `gemini-1.5-flash` (has free tier)
- Anthropic Claude: `anthropic` SDK, `claude-3-5-sonnet` with vision

**Recommended for MVP: Gemini 1.5 Flash** — free tier (1500 requests/day, resets
every 24 hours, permanently free, no credit card needed). 1 request = 1 image scan.
1500/day is more than enough for any demo or real hospital doing 200 patients/day.
Get API key at https://aistudio.google.com — Google account only, no billing setup.

**Cost:**
- Gemini 1.5 Flash: free tier = 1500 req/day, 1M tokens/min. Zero cost for demo/MVP.
  1 request = 1 image scan. 1500/day resets every 24 hours, permanently free.
  A demo or real hospital doing 200 patients/day will never hit this limit.
  No credit card required — API key from https://aistudio.google.com (Google account only).
- GPT-4o: ~$0.01–0.02 per image. More accurate but costs money. Skip for now.
- Claude: similar pricing to GPT-4o. Skip for now.

**Accuracy on handwritten prescriptions:** very high (85–95%+ on real doctor
handwriting in testing across similar medical document tasks).

**Offline support:** NO — requires internet. This conflicts with Module C's
offline-first requirement. Documented tradeoff: Vision LLM = online path;
Tesseract = offline fallback for printed prescriptions.

**Time to implement:** 2–3 days.

**New dependencies:**
```
google-generativeai==0.7.2    # Gemini (recommended, free tier)
openai==1.35.0                 # GPT-4o (optional, higher accuracy)
```

---

### Approach B — Train a Custom HTR Model (HIGH EFFORT, not MVP)

**What it is:** Train a Handwritten Text Recognition (HTR) model specifically on
medical prescription handwriting.

**Architecture:** CRNN (Convolutional Recurrent Neural Network) or TrOCR
(Transformer-based OCR, fine-tuned from Microsoft's pretrained model).
- CNN extracts spatial features from the image
- RNN/Transformer decodes the character sequence
- CTC loss (Connectionist Temporal Classification) handles variable-length output

**Dataset needed:**
- Handwritten prescription images with ground-truth text labels (what is written)
- Minimum viable: ~5,000–10,000 labeled word/line images for reasonable accuracy
- For drug names specifically: even less data is needed if training on a narrow
  vocabulary (just drug names, not arbitrary text)
- Public datasets: IAM Handwriting Database (general English), GNHK (Google),
  some domain-specific sets in medical research papers — but none are large,
  clean, and freely downloadable specifically for Indian medical prescriptions

**Training requirements:**
- GPU: minimum NVIDIA T4 (Google Colab free tier works for small experiments)
- Training time: days to weeks depending on dataset size
- Accuracy ceiling: state-of-the-art on clean handwriting = 85–95% character
  accuracy. On real doctor handwriting (notoriously variable): 60–80% without a
  large, high-quality domain-specific dataset.

**Why this is NOT the right MVP choice:**
- Dataset collection and labeling is a multi-week task on its own
- Model accuracy on Indian doctor handwriting without a specialized dataset
  will likely be worse than the Vision LLM approach
- Offline requirement is satisfied but at the cost of months of ML work
- This is a full research/ML project, not an engineering feature

**When to revisit:** after MVP demo, if offline handwriting support becomes a
hard requirement and there is time + resources to collect/label a dataset.

---

### Approach C — Hybrid (production-grade, post-MVP)

**What it is:** Vision LLM for extraction + local validation.
- Image → Gemini/GPT-4o → raw drug list
- Raw drug list → drug_matcher (fuzzy match + brand resolution + RXCUI lookup)
- Validated drug list → allergy checker + interaction checker
- If offline: fall back to Tesseract (printed prescriptions only)

This is how production medical document processing apps work in practice.
Accuracy of Vision LLM + structured validation is higher than either alone.

---

## 4. Decision for MVP

**Use Approach A (Gemini 1.5 Flash Vision API) for handwritten prescriptions.**

Rationale:
- Zero training required
- Free tier covers all demo/MVP usage
- Handles real Indian prescription handwriting, Bengali+English mix, brand names,
  abbreviations — all the things Tesseract cannot
- 2–3 days to implement vs weeks/months for a trained model
- Accuracy is higher than what a small custom-trained model would achieve

**Documented tradeoff:** online-only for handwritten path. The offline fallback
remains Tesseract for printed prescriptions (already working). Module C's offline
model can be revisited post-MVP if needed.

---

## 5. Implementation Plan (Approach A — Gemini Vision)

### Phase 1 — Setup (half a day)
- [ ] Create Google AI Studio account at https://aistudio.google.com
- [ ] Generate a free API key (no billing needed for free tier)
- [ ] Add `GEMINI_API_KEY` to backend environment / `.env` file
- [ ] `pip install google-generativeai==0.7.2`
- [ ] Test: send one prescription image manually via Python script, verify JSON output

### Phase 2 — Build the service (1 day)
- [ ] Create `backend/app/modules/prescription/services/vision_ocr_service.py`
  - `extract_drugs_from_image(image_bytes) -> list[dict]`
  - Sends image + structured prompt to Gemini 1.5 Flash
  - Parses JSON response → returns `[{name, dosage, frequency}]`
  - Falls back to Tesseract if API call fails (offline/network error)
- [ ] Prompt design (critical): structured prompt that asks for JSON output,
  handles "unable to read" gracefully, specifies to return drug names only
  (not patient info, diagnoses, etc.)

### Phase 3 — Wire into existing pipeline (half a day)
- [ ] Update `router.py` `ocr_audit` endpoint to call `vision_ocr_service` first,
  fall back to `ocr_service` (Tesseract) if Gemini fails or returns empty
- [ ] The drug list from Vision LLM feeds the same `drug_matcher` → allergy/interaction
  checkers — no changes to those services

### Phase 4 — Test
- [ ] Test case 1: handwritten prescription → Vision LLM extracts drugs correctly
- [ ] Test case 2: printed prescription → Tesseract still works (fallback not broken)
- [ ] Test case 3: API key missing / network down → fallback to Tesseract gracefully
- [ ] Test case 4: brand names in handwriting (e.g. "Napa", "Orcef") → extracted
  and resolved to generics by drug_matcher

---

## 6. New File to Create

```
backend/
└── app/
    └── modules/
        └── prescription/
            └── services/
                └── vision_ocr_service.py    # NEW — Gemini Vision extraction
```

`ocr_service.py` (Tesseract) stays unchanged as the offline/printed fallback.

---

## 7. Prompt Design (critical — this determines accuracy)

The prompt sent to Gemini must be structured to get consistent, parseable output.

```python
EXTRACTION_PROMPT = """
You are a medical prescription parser. Extract all prescribed medications from
this prescription image.

Return ONLY a JSON object in this exact format, nothing else:
{
  "drugs": [
    {"name": "drug name as written", "dosage": "e.g. 500mg", "frequency": "e.g. twice daily"},
    ...
  ],
  "confidence": "high|medium|low",
  "notes": "any relevant notes e.g. image quality issues"
}

Rules:
- Include every drug/medicine you can read, even if partially legible
- Use the name exactly as written (brand or generic — do not translate)
- If you cannot read a drug name clearly, include it with a "?" suffix
- Do NOT include diagnoses, patient info, doctor info, or non-drug items
- If the image has no readable prescription content, return {"drugs": [], "confidence": "low"}
"""
```

The drug_matcher then handles brand→generic resolution and fuzzy matching,
so the Vision LLM doesn't need to normalize names — it just extracts what's there.

---

## 8. What This Changes in the Overall Module B Architecture

Before (current state):
```
image → Tesseract OCR → raw text → drug_matcher → drug list → checkers
```

After (with Vision LLM):
```
image → Gemini Vision (primary) ──→ drug list ──→ drug_matcher → checkers
              ↓ (fallback if offline/fail)
        Tesseract OCR → raw text → drug_matcher → checkers
```

Everything downstream (drug_matcher, allergy_checker, interaction_checker,
FastAPI endpoints, Flutter UI) is **unchanged**. Only the OCR entry point changes.

---

## 9. Decisions Made

- Vision LLM (Gemini 1.5 Flash) = PRIMARY OCR path for handwritten prescriptions
- Free tier: 1500 scans/day (1 image = 1 request), resets every 24 hours, no card needed
- Tesseract = FALLBACK for printed prescriptions and offline mode
- drug_matcher handles brand→generic resolution for both paths (unchanged)
- Offline tradeoff explicitly accepted for MVP: handwriting = online-only
- No custom model training for MVP — revisit post-demo if offline HTR needed

---

## 10. Open Questions

- Which Vision LLM to use: Gemini 1.5 Flash (free, recommended) vs GPT-4o
  (more accurate, costs money) vs Claude (similar to GPT-4o)?
- How to handle the API key securely in the project (env variable, .env file,
  not committed to git)?
- Should the Flutter UI show a different indicator when Vision LLM was used
  vs Tesseract (so the user knows it went through the AI path)?
- Post-MVP: if offline HTR becomes required, what dataset strategy to use for
  collecting Indian doctor handwriting samples?
