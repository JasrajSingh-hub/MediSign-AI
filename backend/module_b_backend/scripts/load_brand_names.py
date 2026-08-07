"""Load brand_names.csv into SQLite brand_names table.

Run from backend/:  python scripts/load_brand_names.py
Maps common brand/trade names -> generic ingredient names so the OCR drug
matcher can recognize brand names written on real prescriptions.
"""
import csv
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from app.core.database import DB_PATH, get_connection
from app.modules.prescription.models import CREATE_BRAND_NAMES

CSV_PATH = os.path.join(BACKEND_DIR, "data", "brand_names.csv")


def main():
    conn = get_connection()
    conn.execute(CREATE_BRAND_NAMES)
    conn.execute("DELETE FROM brand_names")   # full refresh on each run

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [(r["brand_name"].strip().lower(), r["generic_name"].strip().lower())
                for r in csv.DictReader(f)]

    conn.executemany(
        "INSERT INTO brand_names (brand_name, generic_name) VALUES (?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} brand -> generic mappings into {DB_PATH}")


if __name__ == "__main__":
    main()
