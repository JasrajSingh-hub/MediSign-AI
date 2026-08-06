"""Load curated alternative-drug mappings into SQLite.

Run from backend/:  python scripts/load_drug_alternatives.py

Idempotent: clears the table first, then re-inserts, so re-running rebuilds it.
Reuses get_connection() and CREATE_DRUG_ALTERNATIVES from the app.
"""
import csv
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from app.core.database import DB_PATH, get_connection
from app.modules.prescription.models import CREATE_DRUG_ALTERNATIVES

CSV_PATH = os.path.join(BACKEND_DIR, "data", "drug_alternatives.csv")


def main():
    conn = get_connection()
    conn.execute(CREATE_DRUG_ALTERNATIVES)
    conn.execute("DELETE FROM drug_alternatives")  # rebuild from CSV each run

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [(r["avoid_class"], r["alternative_drug"], r["alternative_class"],
                 r["indication"], r["note"], r["source"])
                for r in csv.DictReader(f)]
    conn.executemany(
        "INSERT INTO drug_alternatives "
        "(avoid_class, alternative_drug, alternative_class, indication, note, source) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} alternative-drug mappings -> {DB_PATH}")


if __name__ == "__main__":
    main()
