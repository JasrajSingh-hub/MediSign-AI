"""Phase 8 & 9: Doctor Handoff Summary Service (OpenRouter Call #2).

Formats collected triage data and uses OpenRouter (with local deterministic fallback)
to generate a concise, non-diagnostic clinician handoff summary.
"""
import json
import os
import re
from typing import Dict, List
import urllib.request


def generate_local_summary_fallback(
    patient_id: str,
    drugs: List[str],
    context: str,
    answers: Dict[str, str],
    priority: str,
    red_flag_alert: bool,
    triggered_red_flags: List[str],
) -> str:
    """Generate a clean, professional, non-diagnostic clinician handoff report locally."""
    def _clean_key(k: str) -> str:
        clean = k[2:] if k.startswith("q_") or k.startswith("q-") else k
        return clean.replace("_", " ").title()

    formatted_answers = [f"{_clean_key(k)}: {v}" for k, v in answers.items()]
    answers_str = "; ".join(formatted_answers) if formatted_answers else "None reported"

    alert_prefix = f"ALERT - Red flags detected ({', '.join(triggered_red_flags)}). " if red_flag_alert else ""

    summary = (
        f"{alert_prefix}Patient ({patient_id}) presents for {context}. "
        f"Prescribed Medications: {', '.join([d.capitalize() for d in drugs]) if drugs else 'None'}. "
        f"Reported Symptoms & History: {answers_str}. "
        f"Priority Level: {priority}. Recommend clinician review."
    )
    return summary


def generate_doctor_summary(
    patient_id: str,
    drugs: List[str],
    context: str,
    answers: Dict[str, str],
    priority: str,
    red_flag_alert: bool,
    triggered_red_flags: List[str],
) -> str:
    """Generate a polished clinician handoff summary using OpenRouter or local fallback."""
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        return generate_local_summary_fallback(
            patient_id, drugs, context, answers, priority, red_flag_alert, triggered_red_flags
        )

    try:
        formatted_answers = "\n".join([f"- {_clean_key(k)}: {v}" for k, v in answers.items()])
        prompt = f"""
You are an expert clinical medical assistant writing a concise handoff note for an attending physician.

RULES:
1. Do NOT diagnose the patient under any circumstances.
2. Mention only the collected symptom information, prescribed medications, and priority level.
3. Keep the summary under 4 sentences. Be direct, professional, and clear.

Patient ID: {patient_id}
Prescribed Medications: {', '.join(drugs) if drugs else 'None'}
Clinical Context: {context}
Calculated Priority: {priority}
Red Flag Alert: {'YES (' + ', '.join(triggered_red_flags) + ')' if red_flag_alert else 'NO'}

Patient Questionnaire Answers:
{formatted_answers}

Write the concise doctor handoff summary:
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
            content = resp_data["choices"][0]["message"]["content"].strip()
            return content
    except Exception as e:
        print(f"[SUMMARY] LLM API call failed ({e}) — using local summary generator fallback")
        return generate_local_summary_fallback(
            patient_id, drugs, context, answers, priority, red_flag_alert, triggered_red_flags
        )
