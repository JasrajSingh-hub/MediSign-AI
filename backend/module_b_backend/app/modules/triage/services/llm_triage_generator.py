"""Phase 5: OpenRouter / Gemini Context & Question Generator (Cache Miss path).

Executes OpenRouter Call #1 to dynamically generate structured question trees
and emergency red flags for new medicine combinations, then persists to SQLite cache.
"""
import json
import os
import re
from typing import Any, Dict, List, Optional
import urllib.request

from module_b_backend.app.modules.triage.services import cache_service


def generate_fallback_triage(
    drugs: List[str], clinical_ctx: Dict[str, Any], emergency_sign: Optional[str] = None
) -> Dict[str, Any]:
    """Deterministic local fallback generator used if LLM API is unavailable or offline."""
    sign_upper = emergency_sign.upper() if emergency_sign else ""

    if sign_upper == "AMBULANCE":
        return {
            "instant_critical": True,
            "contexts": ["Critical Emergency"],
            "question_categories": ["Immediate Staff Call"],
            "red_flags": ["Ambulance Sign Detected"],
            "question_tree": [],
        }

    if sign_upper == "HEART":
        question_tree = [{
            "id": "q_heart",
            "category": "Cardiovascular",
            "question": "I noticed you signed HEART. What is your primary symptom?",
            "type": "choice",
            "options": ["1: Pain", "2: Tightness", "3: Difficulty Breathing", "0: Other"],
        }]
        return {
            "instant_critical": False,
            "contexts": ["Cardiac Discomfort"],
            "question_categories": ["Chest Symptoms"],
            "red_flags": ["Chest Pain", "Chest Tightness"],
            "question_tree": question_tree,
        }

    if sign_upper in ("BREATHING", "LUNG", "RESPIRATORY"):
        inhaler_note = " (e.g., Salbutamol/Budesonide)" if any("salbutamol" in d.lower() for d in drugs) else ""
        question_tree = [{
            "id": "q_breathing",
            "category": "Respiratory",
            "question": f"I noticed you signed BREATHING. Is your medication/inhaler{inhaler_note} helping?",
            "type": "choice",
            "options": ["1: Yes", "2: No", "0: Other"],
        }]
        return {
            "instant_critical": False,
            "contexts": ["Respiratory Distress"],
            "question_categories": ["Shortness of Breath"],
            "red_flags": ["Severe Breathlessness", "Cyanosis"],
            "question_tree": question_tree,
        }

    if sign_upper == "KNEE":
        question_tree = [{
            "id": "q_knee",
            "category": "Musculoskeletal",
            "question": "I noticed you signed KNEE. What is the problem?",
            "type": "choice",
            "options": ["1: Pain", "2: Swelling", "3: Injury", "4: Cannot Move", "0: Other"],
        }]
        return {
            "instant_critical": False,
            "contexts": ["Joint Discomfort"],
            "question_categories": ["Knee Pain"],
            "red_flags": ["Inability to Weight Bear"],
            "question_tree": question_tree,
        }

    indications = clinical_ctx.get("aggregated_indications", ["Symptom Relief"])
    symptoms = clinical_ctx.get("aggregated_symptoms", ["General Discomfort"])
    red_flags = clinical_ctx.get("aggregated_red_flags", ["Difficulty Breathing", "Severe Pain"])

    contexts = indications[:2] if indications else ["General Medical Consultation"]
    categories = symptoms[:3] if symptoms else ["Fever", "Pain", "General Symptoms"]

    question_tree = [
        {
            "id": "q_fever",
            "category": "Fever",
            "question": "Do you currently have a fever or elevated body temperature?",
            "type": "choice",
            "options": ["Yes", "No"],
            "follow_up": {
                "Yes": {
                    "id": "q_fever_duration",
                    "question": "How many days have you experienced fever?",
                    "options": ["1 Day", "2 Days", "3 Days or more"],
                }
            },
        },
        {
            "id": "q_cough",
            "category": "Cough",
            "question": "Do you have a cough or respiratory discomfort?",
            "type": "choice",
            "options": ["Yes", "No"],
            "follow_up": {
                "Yes": {
                    "id": "q_cough_type",
                    "question": "Is your cough dry or producing mucus/phlegm?",
                    "options": ["Dry Cough", "Productive Cough (Phlegm)"],
                }
            },
        },
        {
            "id": "q_red_flag",
            "category": "Emergency",
            "question": "Are you experiencing any severe symptoms such as difficulty breathing or chest pain?",
            "type": "choice",
            "options": ["Yes", "No"],
        },
    ]

    return {
        "instant_critical": False,
        "contexts": contexts,
        "question_categories": categories,
        "red_flags": red_flags,
        "question_tree": question_tree,
    }


def generate_triage_context_llm(
    drugs: List[str],
    clinical_ctx: Dict[str, Any],
    signature: str,
    domain_signature: str,
    emergency_sign: Optional[str] = None,
) -> Dict[str, Any]:
    """Call OpenRouter (or fallback to local deterministic generator) on Cache MISS."""
    if emergency_sign and emergency_sign.upper() == "AMBULANCE":
        return generate_fallback_triage(drugs, clinical_ctx, emergency_sign)

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("[TRIAGE] No OpenRouter/Gemini API key found — using local deterministic generator")
        result = generate_fallback_triage(drugs, clinical_ctx, emergency_sign)
    else:
        try:
            sign_prompt = f"\nPatient Detected Emergency Sign: {emergency_sign}" if emergency_sign else ""
            prompt = f"""
You are an expert clinical triage AI assistant.
{sign_prompt}
Prescribed Generic Medicines: {', '.join(drugs) if drugs else 'None'}
Therapeutic Classes: {', '.join(clinical_ctx.get('therapeutic_domains', []))}
Common Indications: {', '.join(clinical_ctx.get('aggregated_indications', []))}
Known Red Flags: {', '.join(clinical_ctx.get('aggregated_red_flags', []))}

Generate a JSON object for a patient symptom questionnaire with EXACTLY this structure:
{{
    "instant_critical": false,
    "contexts": ["Primary Condition/Context 1", "Primary Condition/Context 2"],
    "question_categories": ["Category 1", "Category 2", "Category 3"],
    "red_flags": ["Red Flag 1", "Red Flag 2"],
    "question_tree": [
        {{
            "id": "q1",
            "category": "Symptom",
            "question": "Patient-facing follow-up question acknowledging their sign/prescription?",
            "type": "choice",
            "options": ["1: Option A", "2: Option B", "0: Other"]
        }}
    ]
}}

Return ONLY valid raw JSON. No markdown formatting, no explanation.
"""
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            payload = json.dumps({
                "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                content = resp_data["choices"][0]["message"]["content"]
                
                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    result = generate_fallback_triage(drugs, clinical_ctx, emergency_sign)
        except Exception as e:
            print(f"[TRIAGE] LLM API call failed ({e}) — falling back to deterministic generator")
            result = generate_fallback_triage(drugs, clinical_ctx, emergency_sign)

    cache_service.save_to_cache(
        signature=signature,
        domain_signature=domain_signature,
        drugs=drugs,
        contexts=result.get("contexts", []),
        question_categories=result.get("question_categories", []),
        question_tree=result.get("question_tree", []),
        red_flags=result.get("red_flags", []),
    )

    return result
