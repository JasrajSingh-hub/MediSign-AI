"""DB queries for allergy checking. Pure SQLite (sqlite3 stdlib) — no ORM."""
from module_b_backend.app.core.database import get_connection


def get_drug_class(name: str):
    """Return the curated allergy_class for a drug name, or None if unknown."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT allergy_class FROM drug_allergy_classes "
            "WHERE lower(ingredient_name) = lower(?)",
            (name,),
        ).fetchone()
        return row["allergy_class"] if row else None
    finally:
        conn.close()


def get_patient_allergy_classes(patient_id: str):
    """Return the list of allergy classes a patient is allergic to."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT allergen_class FROM patient_allergies WHERE patient_id = ?",
            (patient_id,),
        ).fetchall()
        return [r["allergen_class"] for r in rows]
    finally:
        conn.close()


def add_patient_allergy(patient_id, allergen_class, allergen_text,
                        severity="unknown", source="curated"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO patient_allergies "
            "(patient_id, allergen_class, allergen_text, severity, source) "
            "VALUES (?, ?, ?, ?, ?)",
            (patient_id, allergen_class, allergen_text, severity, source),
        )
        conn.commit()
    finally:
        conn.close()


def get_interaction(drug_a: str, drug_b: str):
    """Return the curated interaction row for a pair, or None if none known.

    Order-independent: (warfarin, aspirin) == (aspirin, warfarin). Lookup is
    case-insensitive, so the request casing doesn't matter.
    """
    a, b = drug_a.lower(), drug_b.lower()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT drug_a, drug_b, rxcui_a, rxcui_b, severity, description, "
            "mechanism, source FROM drug_interactions "
            "WHERE (lower(drug_a) = ? AND lower(drug_b) = ?) "
            "   OR (lower(drug_a) = ? AND lower(drug_b) = ?)",
            (a, b, b, a),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_known_drug_names():
    """Return every drug name we can recognize, for OCR fuzzy-matching.

    Combines the curated allergy-class drugs with the interaction-table drug
    names. (Coverage is expanded by the RxNorm bulk dictionary upgrade.)
    """
    conn = get_connection()
    try:
        names = set()
        for row in conn.execute("SELECT ingredient_name FROM drug_allergy_classes"):
            names.add(row["ingredient_name"])
        for row in conn.execute("SELECT drug_a, drug_b FROM drug_interactions"):
            names.add(row["drug_a"])
            names.add(row["drug_b"])
        return sorted(names)
    finally:
        conn.close()


def get_brand_map():
    """Return {brand_name(lower): generic_name(lower)} for OCR brand resolution.

    Empty dict if the table doesn't exist yet (loader not run) — callers then
    simply fall back to generic-only matching.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='brand_names'"
        ).fetchall()
        if not rows:
            return {}
        return {
            r["brand_name"].lower(): r["generic_name"].lower()
            for r in conn.execute("SELECT brand_name, generic_name FROM brand_names")
        }
    finally:
        conn.close()


def get_alternatives(avoid_class: str):
    """Return all curated alternative drugs suggested when a patient is allergic
    to `avoid_class`. Caller is responsible for excluding alternatives the patient
    is also allergic to.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT alternative_drug, alternative_class, indication, note "
            "FROM drug_alternatives WHERE lower(avoid_class) = lower(?)",
            (avoid_class,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_drug_class(ingredient_name: str, allergy_class: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO drug_allergy_classes (ingredient_name, allergy_class) VALUES (?, ?)",
            (ingredient_name.lower(), allergy_class),
        )
        conn.commit()
    finally:
        conn.close()


def add_brand_mapping(brand_name: str, generic_name: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO brand_names (brand_name, generic_name) VALUES (?, ?)",
            (brand_name.lower(), generic_name.lower()),
        )
        conn.commit()
    finally:
        conn.close()

