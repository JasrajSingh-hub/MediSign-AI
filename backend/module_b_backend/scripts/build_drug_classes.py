"""
build_drug_classes.py  —  Phase 3.4 of Module B (Allergy Detection)

Batch-resolves a curated list of common, allergy-relevant drugs through
resolve_drug_to_class() and saves the RAW result to:
    backend/data/drug_classes.json

Phase 4 is where YOU hand-pick ONE clean allergy class per drug from this
raw data (e.g. amoxicillin -> "Penicillins") and turn it into the curated
CSV / SQLite table.

RUN:  python build_drug_classes.py
"""

import json
import os

from rxnorm_resolver import resolve_drug_to_class

# ~25 common, allergy-relevant drugs spanning the major drug classes.
DRUG_LIST = [
    # Penicillins
    "amoxicillin", "ampicillin", "penicillin v",
    # Cephalosporins
    "cephalexin", "ceftriaxone",
    # Fluoroquinolones
    "ciprofloxacin", "levofloxacin",
    # Macrolides
    "azithromycin", "clarithromycin",
    # Sulfonamides
    "sulfamethoxazole", "trimethoprim",
    # NSAIDs
    "ibuprofen", "naproxen", "aspirin", "acetaminophen",
    # Anticoagulants
    "warfarin", "heparin", "clopidogrel",
    # Other common
    "metformin", "lisinopril", "atorvastatin", "omeprazole",
    # Opioids / other
    "morphine", "codeine", "vancomycin",
]

# Save next to this script: backend/data/drug_classes.json
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "drug_classes.json")


def main():
    results = []
    for name in DRUG_LIST:
        entry = resolve_drug_to_class(name)
        results.append(entry)
        print(f"  {name:18s} -> {str(entry['rxcui']):>6}  ({len(entry['classes'])} classes)")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(results)} drugs -> {os.path.abspath(OUTPUT_PATH)}")


if __name__ == "__main__":
    main()
