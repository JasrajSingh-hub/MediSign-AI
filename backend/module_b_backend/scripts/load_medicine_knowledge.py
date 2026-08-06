"""Load medicine_knowledge.csv into SQLite rxnorm_local.db and create reasoning_cache table.

Run from backend/: python scripts/load_medicine_knowledge.py
"""
import csv
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from module_b_backend.app.core.database import DB_PATH, get_connection
from module_b_backend.app.modules.prescription.models import CREATE_MEDICINE_KNOWLEDGE, CREATE_REASONING_CACHE

CSV_PATH = os.path.join(BACKEND_DIR, "data", "medicine_knowledge.csv")


def main():
    conn = get_connection()
    conn.execute(CREATE_MEDICINE_KNOWLEDGE)
    conn.execute(CREATE_REASONING_CACHE)

    conn.execute("DELETE FROM medicine_knowledge")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [
            (
                r["generic_name"].strip().lower(),
                r["drug_class"].strip(),
                r["therapeutic_class"].strip(),
                r["common_indications"].strip(),
                r["body_system"].strip(),
                r["common_symptoms"].strip(),
                r["red_flag_symptoms"].strip(),
            )
            for r in csv.DictReader(f)
        ]

    conn.executemany(
        """INSERT OR REPLACE INTO medicine_knowledge 
        (generic_name, drug_class, therapeutic_class, common_indications, body_system, common_symptoms, red_flag_symptoms)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )

    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} medicine knowledge entries & initialized reasoning_cache table -> {DB_PATH}")


if __name__ == "__main__":
    main()
