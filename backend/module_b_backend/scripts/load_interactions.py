"""Load the curated drug-interaction CSV into SQLite.

Run from backend/:  python scripts/load_interactions.py

Idempotent: clears the table first, then re-inserts, so re-running rebuilds it.
Reuses get_connection() and the CREATE_DRUG_INTERACTIONS DDL from the app.
"""
import csv
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from module_b_backend.app.core.database import DB_PATH, get_connection
from module_b_backend.app.modules.prescription.models import CREATE_DRUG_INTERACTIONS

CSV_PATH = os.path.join(BACKEND_DIR, "data", "drug_interactions.csv")


def main():
    conn = get_connection()
    conn.execute(CREATE_DRUG_INTERACTIONS)
    conn.execute("DELETE FROM drug_interactions")  # rebuild from CSV each run

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [(r["drug_a"], r["drug_b"], r["rxcui_a"], r["rxcui_b"],
                 r["severity"], r["description"], r["mechanism"], r["source"])
                for r in csv.DictReader(f)]
    conn.executemany(
        "INSERT INTO drug_interactions "
        "(drug_a, drug_b, rxcui_a, rxcui_b, severity, description, mechanism, source) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} drug interactions -> {DB_PATH}")


if __name__ == "__main__":
    main()
