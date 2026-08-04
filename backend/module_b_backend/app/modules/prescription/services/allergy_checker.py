from .. import repository


def check_allergies(patient_id: str, prescribed_drugs: list):
    patient_classes = set(repository.get_patient_allergy_classes(patient_id))

    conflicts = []
    safe = []
    for drug in prescribed_drugs:
        drug_class = repository.get_drug_class(drug)
        if drug_class is None:
            safe.append({"drug": drug, "note": "class not found in local table"})
            continue
        if drug_class in patient_classes:
            raw_alts = repository.get_alternatives(drug_class)
            suggestions = [
                {
                    "alternative_drug": a["alternative_drug"],
                    "alternative_class": a["alternative_class"],
                    "indication": a["indication"],
                    "note": a["note"] or "",
                }
                for a in raw_alts
                if a["alternative_class"].lower() not in {c.lower() for c in patient_classes}
            ]
            conflicts.append({
                "drug": drug,
                "matched_class": drug_class,
                "allergy_class": drug_class,
                "alternatives": suggestions,
            })
        else:
            safe.append({"drug": drug, "class": drug_class})
    return {"patient_id": patient_id, "conflicts": conflicts, "safe": safe}

