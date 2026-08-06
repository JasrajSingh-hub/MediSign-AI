"""Phase 2: Context Builder Service (Offline, No AI).

Builds aggregated clinical context (indications, symptoms, therapeutic domains)
from local SQLite medicine_knowledge for a list of prescribed generic drugs.
"""
from typing import Any, Dict, List
from module_b_backend.app.modules.triage import repository


def build_clinical_context(prescribed_drugs: List[str]) -> Dict[str, Any]:
    """Aggregate knowledge base details for prescribed drugs."""
    cleaned_drugs = [d.strip().lower() for d in prescribed_drugs if d.strip()]
    knowledge_entries = repository.get_medicine_knowledge(cleaned_drugs)
    
    known_map = {entry["generic_name"]: entry for entry in knowledge_entries}
    
    medicine_summaries = []
    all_indications = set()
    all_symptoms = set()
    all_red_flags = set()
    therapeutic_domains = set()

    for drug in cleaned_drugs:
        if drug in known_map:
            k = known_map[drug]
            medicine_summaries.append({
                "generic": k["generic_name"].capitalize(),
                "drug_class": k["drug_class"],
                "therapeutic_class": k["therapeutic_class"],
                "uses": k["common_indications"],
                "symptoms": k["common_symptoms"],
                "red_flags": k["red_flag_symptoms"],
            })
            all_indications.update(k["common_indications"])
            all_symptoms.update(k["common_symptoms"])
            all_red_flags.update(k["red_flag_symptoms"])
            therapeutic_domains.add(k["therapeutic_class"])
        else:
            medicine_summaries.append({
                "generic": drug.capitalize(),
                "drug_class": "General Medication",
                "therapeutic_class": "General Symptom Relief",
                "uses": ["Symptom Management"],
                "symptoms": ["General Discomfort"],
                "red_flags": ["Severe Pain", "Difficulty Breathing"],
            })
            all_indications.add("Symptom Management")
            all_symptoms.add("General Discomfort")
            all_red_flags.update(["Severe Pain", "Difficulty Breathing"])
            therapeutic_domains.add("General Symptom Relief")

    return {
        "prescribed_drugs": [d.capitalize() for d in cleaned_drugs],
        "medicine_details": medicine_summaries,
        "therapeutic_domains": sorted(list(therapeutic_domains)),
        "aggregated_indications": sorted(list(all_indications)),
        "aggregated_symptoms": sorted(list(all_symptoms)),
        "aggregated_red_flags": sorted(list(all_red_flags)),
    }
