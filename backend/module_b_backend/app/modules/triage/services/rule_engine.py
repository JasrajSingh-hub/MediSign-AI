"""Phase 7: Rule Engine (Local Priority Logic — Offline, No AI).

Evaluates patient questionnaire answers against symptom duration and red flags
to categorize priority as LOW, MEDIUM, HIGH, or CRITICAL.
"""
from typing import Any, Dict, List, Tuple

DEFAULT_RED_FLAGS = [
    "difficulty breathing",
    "breathlessness",
    "chest pain",
    "black tarry stool",
    "vomiting blood",
    "confusion",
    "jaundice",
    "anaphylaxis",
    "swelling of throat",
    "severe dizziness",
    "fainting",
]


def evaluate_triage_priority(
    answers: Dict[str, str], known_red_flags: List[str] = None
) -> Tuple[str, bool, List[str]]:
    """Evaluate patient answers to return (priority, red_flag_alert, triggered_red_flags)."""
    all_red_flags = set(DEFAULT_RED_FLAGS)
    if known_red_flags:
        for rf in known_red_flags:
            all_red_flags.add(rf.strip().lower())

    triggered_red_flags = []
    answers_clean = {k.strip().lower(): v.strip().lower() for k, v in answers.items()}

    for key, val in answers_clean.items():
        clean_key = key.replace("_", " ")
        if val in ("yes", "true", "severe", "1: yes"):
            if "red flag" in clean_key or "emergency" in clean_key:
                triggered_red_flags.append("Severe Symptoms (Difficulty Breathing / Chest Pain)")
            for rf in all_red_flags:
                if rf in clean_key:
                    triggered_red_flags.append(rf.title())
        for rf in all_red_flags:
            if rf in val and val not in ("yes", "no"):
                triggered_red_flags.append(rf.title())

    triggered_red_flags = sorted(list(set(triggered_red_flags)))

    if triggered_red_flags:
        return "HIGH", True, triggered_red_flags

    has_fever = any(v in ("yes", "true", "1: yes") for k, v in answers_clean.items() if "fever" in k and "duration" not in k)
    has_cough = any(v in ("yes", "true", "1: yes") for k, v in answers_clean.items() if "cough" in k and "type" not in k)
    
    is_persistent = any("3 day" in v or "4 day" in v or "5 day" in v or "week" in v for v in answers_clean.values())

    if is_persistent and (has_fever or has_cough):
        return "MEDIUM", False, []

    if has_fever and has_cough:
        return "MEDIUM", False, []

    if is_persistent:
        return "MEDIUM", False, []

    return "LOW", False, []
