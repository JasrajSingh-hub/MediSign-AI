"""Phase 4.3 — load the curated CSV into SQLite and seed a demo patient.

Run from backend/:  python scripts/load_drug_classes.py
"""
import csv
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from module_b_backend.app.core.database import DB_PATH, get_connection
from module_b_backend.app.modules.prescription.models import CREATE_DRUG_CLASSES, CREATE_PATIENT_ALLERGIES

CSV_PATH = os.path.join(BACKEND_DIR, "data", "drug_allergy_classes.csv")


def main():
    conn = get_connection()
    conn.execute(CREATE_DRUG_CLASSES)
    conn.execute(CREATE_PATIENT_ALLERGIES)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [(r["ingredient_name"], r["rxcui"], r["allergy_class"])
                for r in csv.DictReader(f)]
    conn.executemany(
        "INSERT INTO drug_allergy_classes (ingredient_name, rxcui, allergy_class) VALUES (?, ?, ?)",
        rows,
    )

    # Seed a demo patient (P001) allergic to Penicillins — used by tests/demo.
    conn.execute("DELETE FROM patient_allergies WHERE patient_id = 'P001'")
    conn.execute(
        "INSERT INTO patient_allergies "
        "(patient_id, allergen_class, allergen_text, severity, source) "
        "VALUES (?, ?, ?, ?, ?)",
        ("P001", "Penicillins", "Penicillin", "severe", "curated"),
    )

    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} drug classes + seeded patient P001 -> {DB_PATH}")


if __name__ == "__main__":
    main()
