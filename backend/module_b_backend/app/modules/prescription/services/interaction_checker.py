from itertools import combinations

from .. import repository

SEVERITY_ORDER = {"CONTRAINDICATED": 0, "MAJOR": 1, "MODERATE": 2, "MINOR": 3}


def check_interactions(patient_id: str, prescribed_drugs: list):
    conflicts = []
    safe = set(prescribed_drugs)

    for a, b in combinations(sorted(prescribed_drugs), 2):
        row = repository.get_interaction(a, b)
        if row:
            conflicts.append({
                "drug_a": row["drug_a"],
                "drug_b": row["drug_b"],
                "severity": row["severity"],
                "description": row["description"],
                "mechanism": row["mechanism"] or "",
            })
            safe.discard(a)
            safe.discard(b)

    conflicts.sort(key=lambda c: SEVERITY_ORDER.get(c["severity"], 99))
    return {
        "patient_id": patient_id,
        "interactions": conflicts,
        "safe": sorted(safe),
    }

