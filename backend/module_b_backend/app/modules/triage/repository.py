"""SQLite repository queries for medicine_knowledge and reasoning_cache tables."""
import json
from typing import Any, Dict, List, Optional
from module_b_backend.app.core.database import get_connection


def get_medicine_knowledge(generic_names: List[str]) -> List[Dict[str, Any]]:
    """Fetch medicine knowledge details for a list of generic drug names."""
    if not generic_names:
        return []
    
    conn = get_connection()

    placeholders = ",".join(["?"] * len(generic_names))
    query = f"""
    SELECT generic_name, drug_class, therapeutic_class, common_indications, body_system, common_symptoms, red_flag_symptoms
    FROM medicine_knowledge
    WHERE lower(generic_name) IN ({placeholders})
    """
    cleaned_names = [n.strip().lower() for n in generic_names]
    cursor = conn.execute(query, cleaned_names)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        # Support dict-like indexing or tuple indexing
        g_name = r["generic_name"] if isinstance(r, dict) or hasattr(r, "keys") else r[0]
        d_class = r["drug_class"] if isinstance(r, dict) or hasattr(r, "keys") else r[1]
        t_class = r["therapeutic_class"] if isinstance(r, dict) or hasattr(r, "keys") else r[2]
        c_ind = r["common_indications"] if isinstance(r, dict) or hasattr(r, "keys") else r[3]
        b_sys = r["body_system"] if isinstance(r, dict) or hasattr(r, "keys") else r[4]
        c_sym = r["common_symptoms"] if isinstance(r, dict) or hasattr(r, "keys") else r[5]
        rf_sym = r["red_flag_symptoms"] if isinstance(r, dict) or hasattr(r, "keys") else r[6]

        results.append({
            "generic_name": g_name,
            "drug_class": d_class,
            "therapeutic_class": t_class,
            "common_indications": [x.strip() for x in c_ind.split("|") if x.strip()] if c_ind else [],
            "body_system": b_sys,
            "common_symptoms": [x.strip() for x in c_sym.split("|") if x.strip()] if c_sym else [],
            "red_flag_symptoms": [x.strip() for x in rf_sym.split("|") if x.strip()] if rf_sym else [],
        })

    return results


def get_reasoning_cache_by_signature(signature: str) -> Optional[Dict[str, Any]]:
    """Lookup cache by exact medicine signature hash."""
    conn = get_connection()
    cursor = conn.execute(
        """SELECT signature, domain_signature, medicines_json, contexts_json, question_categories, question_tree_json, red_flags_json
           FROM reasoning_cache WHERE signature = ?""",
        (signature,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "signature": row[0],
        "domain_signature": row[1],
        "medicines": json.loads(row[2]) if row[2] else [],
        "contexts": json.loads(row[3]) if row[3] else [],
        "question_categories": json.loads(row[4]) if row[4] else [],
        "question_tree": json.loads(row[5]) if row[5] else [],
        "red_flags": json.loads(row[6]) if row[6] else [],
    }


def get_reasoning_cache_by_domain_signature(domain_signature: str) -> Optional[Dict[str, Any]]:
    """Lookup cache by normalized therapeutic domain signature hash (fallback cache hit)."""
    conn = get_connection()
    cursor = conn.execute(
        """SELECT signature, domain_signature, medicines_json, contexts_json, question_categories, question_tree_json, red_flags_json
           FROM reasoning_cache WHERE domain_signature = ? ORDER BY created_at DESC LIMIT 1""",
        (domain_signature,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "signature": row[0],
        "domain_signature": row[1],
        "medicines": json.loads(row[2]) if row[2] else [],
        "contexts": json.loads(row[3]) if row[3] else [],
        "question_categories": json.loads(row[4]) if row[4] else [],
        "question_tree": json.loads(row[5]) if row[5] else [],
        "red_flags": json.loads(row[6]) if row[6] else [],
    }


def save_reasoning_cache(
    signature: str,
    domain_signature: str,
    medicines: List[str],
    contexts: List[str],
    question_categories: List[str],
    question_tree: List[Dict[str, Any]],
    red_flags: List[str],
) -> None:
    """Save or update a reasoning cache entry in SQLite."""
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO reasoning_cache 
           (signature, domain_signature, medicines_json, contexts_json, question_categories, question_tree_json, red_flags_json)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            signature,
            domain_signature,
            json.dumps(medicines),
            json.dumps(contexts),
            json.dumps(question_categories),
            json.dumps(question_tree),
            json.dumps(red_flags),
        ),
    )
    conn.commit()
    conn.close()
