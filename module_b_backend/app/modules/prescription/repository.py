from app.core.database import get_connection


def get_drug_class(name: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT allergy_class FROM drug_allergy_classes WHERE lower(ingredient_name) = lower(?)",
            (name,),
        ).fetchone()
        return row["allergy_class"] if row else None
    finally:
        conn.close()


def get_patient_allergy_classes(patient_id: str):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT allergen_class FROM patient_allergies WHERE patient_id = ?",
            (patient_id,),
        ).fetchall()
        return [r["allergen_class"] for r in rows]
    finally:
        conn.close()


def get_interaction(drug_a: str, drug_b: str):
    a, b = drug_a.lower(), drug_b.lower()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT drug_a, drug_b, rxcui_a, rxcui_b, severity, description, mechanism, source "
            "FROM drug_interactions "
            "WHERE (lower(drug_a) = ? AND lower(drug_b) = ?) OR (lower(drug_a) = ? AND lower(drug_b) = ?)",
            (a, b, b, a),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_known_drug_names():
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
    conn = get_connection()
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='brand_names'").fetchall()
        if not rows:
            return {}
        return {r["brand_name"].lower(): r["generic_name"].lower() for r in conn.execute("SELECT brand_name, generic_name FROM brand_names")}
    finally:
        conn.close()


def get_alternatives(avoid_class: str):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT alternative_drug, alternative_class, indication, note FROM drug_alternatives WHERE lower(avoid_class) = lower(?)",
            (avoid_class,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

