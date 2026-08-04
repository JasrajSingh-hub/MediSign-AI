import re

from rapidfuzz import fuzz, process

from .. import repository

CONFIDENT = 88
UNVERIFIED = 80

_STOPWORDS = {
    "tablet", "tablets", "tab", "cap", "capsule", "capsules", "mg", "ml", "mcg",
    "once", "twice", "thrice", "daily", "day", "days", "week", "morning",
    "night", "evening", "before", "after", "food", "meal", "take", "oral",
    "dose", "dosage", "times", "hrs", "hours", "prescription", "rx", "dr",
    "patient", "name", "date", "sig", "qty", "refill", "signature",
    "drop", "drops", "ointment", "cream", "syrup", "injection", "inj",
    "extend", "plus", "forte", "extra", "relief", "advance",
}

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-]{2,}")


def _candidates(text: str):
    clean_lines = []
    for line in text.splitlines():
        if not line.strip():
            continue
        ascii_chars = sum(1 for c in line if ord(c) < 128)
        if ascii_chars / len(line) > 0.5:
            clean_lines.append(line)
    clean_text = " ".join(clean_lines)

    seen = []
    for raw in _TOKEN_RE.findall(clean_text):
        w = raw.lower().strip("-")
        if len(w) < 4 or w in _STOPWORDS:
            continue
        if w not in seen:
            seen.append(w)
    return seen


def match_drugs(text: str):
    known = repository.get_known_drug_names()
    if not known:
        return [], []

    brand_map = repository.get_brand_map()
    search_terms = list(known) + list(brand_map.keys())

    tokens = _candidates(text)
    matched = {}

    for tok in tokens:
        best = process.extractOne(tok, search_terms, scorer=fuzz.token_set_ratio)
        if best is None:
            continue
        name, score, _ = best
        if score < UNVERIFIED:
            continue

        if name in brand_map:
            generic = brand_map[name]
            brand = name
        else:
            generic = name
            brand = ""

        status = "confident" if score >= CONFIDENT else "unverified"
        prev = matched.get(generic)
        if prev is None or score > prev["confidence"]:
            matched[generic] = {
                "input_token": tok,
                "matched_drug": generic,
                "confidence": round(float(score), 1),
                "status": status,
                "brand": brand,
            }

    return list(matched.values()), tokens

