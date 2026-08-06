import base64
import json
import logging
import os
import re

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
PRIMARY_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"
FALLBACK_MODEL = "openrouter/free"

_PROMPT = """You are a medical prescription parser with pharmacology expertise.
Extract all prescribed medications from this prescription image.

Return ONLY a valid JSON object in this exact format, nothing else:
{
  "drugs": [
    {"name": "generic ingredient name", "brand": "brand name as written", "dosage": "e.g. 500mg", "frequency": "e.g. twice daily", "drug_class": "pharmacological or allergy class e.g. Penicillins, NSAID, Beta-blocker"},
    ...
  ],
  "confidence": "high|medium|low",
  "notes": "any relevant notes"
}

Critical rules:
- For EACH drug, provide the GENERIC/INGREDIENT name
- Also record the brand name exactly as written on the prescription in the "brand" field
- Provide the primary pharmacological/allergy drug class in "drug_class"
- If you cannot determine the generic name, use the brand name as written and mark it with "?" suffix
- Include every drug/medicine visible, even if partially legible
- Do NOT include diagnoses, patient name, doctor info, dates, or non-drug items
- Dosage and frequency are optional — leave as "" if not readable
- If no drugs found: {"drugs": [], "confidence": "low", "notes": "reason"}
- Do not wrap JSON in markdown code blocks"""


def _parse_response(text: str) -> list[dict]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        drugs = data.get("drugs", [])
        if not isinstance(drugs, list):
            return []
        result = []
        for d in drugs:
            if not isinstance(d, dict):
                continue
            name = str(d.get("name", "")).strip()
            if not name:
                continue
            result.append({
                "name": name,
                "brand": str(d.get("brand", "")).strip(),
                "dosage": str(d.get("dosage", "")).strip(),
                "frequency": str(d.get("frequency", "")).strip(),
                "drug_class": str(d.get("drug_class", "")).strip(),
            })
        return result
    except (json.JSONDecodeError, ValueError):
        logger.warning("Vision model returned non-JSON: %s", text[:300])
        return []


def _call_openrouter(image_bytes: bytes, model: str, api_key: str) -> list[dict]:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    if image_bytes[:4] == b'\x89PNG':
        mime = "image/png"
    elif image_bytes[:2] == b'\xff\xd8':
        mime = "image/jpeg"
    else:
        mime = "image/jpeg"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": _PROMPT}
                ]
            }
        ],
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://medisign-ai.local",
        "X-Title": "MediSign AI",
    }

    with httpx.Client(timeout=90.0) as client:
        resp = client.post(OPENROUTER_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_response(content)


def extract_drugs(image_bytes: bytes) -> tuple[list[dict], str]:
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if openrouter_key:
        for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
            try:
                drugs = _call_openrouter(image_bytes, model, openrouter_key)
                if drugs:
                    logger.info("OpenRouter (%s) extracted %d drug(s)", model, len(drugs))
                    return drugs, "vision"
            except Exception as e:
                logger.warning("OpenRouter (%s) failed: %s", model, e)
                continue
    logger.info("All vision models failed — falling back to Tesseract")
    return [], "fallback"


def drug_names_from_image(image_bytes: bytes) -> tuple[list[str], str, str]:
    drugs, source = extract_drugs(image_bytes)
    if source == "fallback" or not drugs:
        return [], "", "fallback"
    names = [d["name"] for d in drugs]
    lines = []
    for d in drugs:
        line = d["name"]
        if d["brand"] and d["brand"] != d["name"]:
            line += f"  (brand: {d['brand']})"
        if d["dosage"]:
            line += f"  {d['dosage']}"
        if d["frequency"]:
            line += f"  ({d['frequency']})"
        lines.append(line)
    return names, "\n".join(lines), "vision"

