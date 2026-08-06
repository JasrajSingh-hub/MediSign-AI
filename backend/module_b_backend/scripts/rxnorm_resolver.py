"""
rxnorm_resolver.py  —  Phase 3.1 + 3.2 + 3.3 of Module B (Allergy Detection)

3.1  get_rxcui(name)            -> drug NAME -> RXCUI
3.2  get_drug_classes(rxcui)    -> RXCUI -> drug CLASSES (deduped)
3.3  resolve_drug_to_class(name)-> NAME -> {rxcui, classes}  (chains 3.1 + 3.2)

RUN:  python rxnorm_resolver.py
(standard library only — no pip install needed)
"""

import json
import urllib.parse
import urllib.request
from typing import Optional

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"

# RxClass returns MANY classification systems. We only keep the ones that say
# "what kind of drug this IS" — because allergies are to a KIND of drug
# (e.g. "Penicillins"), not to a disease it treats or how it's metabolized.
#
#   CHEM     -> chemical ingredient class (e.g. "Penicillins")
#   VA       -> VA pharmacologic class (e.g. "PENICILLINS,AMINO DERIVATIVES")
#   EPC      -> Established Pharmacologic Class (e.g. "Penicillin-class Antibacterial")
#   MOA      -> Mechanism of Action
#   ATC1-4   -> Anatomical Therapeutic Chemical class
# We deliberately DROP: DISEASE (indications), PK/PE/TC (how it acts in body),
#                       STRUCT/DISPOS (structural/disposition).
ALLERGY_RELEVANT_TYPES = ("CHEM", "VA", "EPC", "MOA", "ATC1-4")


def get_rxcui(drug_name: str) -> Optional[str]:
    """3.1 — drug NAME -> RXCUI.  e.g. "amoxicillin" -> "723"

    Calls:  https://rxnav.nlm.nih.gov/REST/rxcui.json?name=amoxicillin
    Returns a dict shaped like:  {"idGroup": {"rxnormId": ["723"]}}
    The RXCUI(s) live at  data["idGroup"]["rxnormId"]  (a list).
    """
    url = RXNORM_BASE + "/rxcui.json?name=" + urllib.parse.quote(drug_name)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [error] {drug_name}: {e}")
        return None
    rxcuis = data.get("idGroup", {}).get("rxnormId", [])
    return rxcuis[0] if rxcuis else None


def get_drug_classes(rxcui: str) -> list:
    """3.2 — RXCUI -> list of {class_id, class_name, class_type} (DEDUPED).

    Calls:  https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui=723

    IMPORTANT: RxClass repeats the same class once per drug-concept (every dose
    form / combo pack of the drug). We dedupe by classId so the output is clean
    and ready for Phase 4 (hand-picking one allergy class per drug).
    """
    url = RXNORM_BASE + f"/rxclass/class/byRxcui.json?rxcui={rxcui}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [error] rxcui {rxcui}: {e}")
        return []

    result = []
    seen_ids = set()  # tracks classIds we've already added
    infos = data.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", [])
    for info in infos:
        concept = info.get("rxclassMinConceptItem", {})
        if concept.get("classType") in ALLERGY_RELEVANT_TYPES:
            cid = concept.get("classId")
            if cid in seen_ids:
                continue  # skip the duplicate
            seen_ids.add(cid)
            result.append({
                "class_id": cid,
                "class_name": concept.get("className"),
                "class_type": concept.get("classType"),
            })
    return result


def resolve_drug_to_class(drug_name: str) -> dict:
    """3.3 — CHAIN 3.1 + 3.2: drug NAME -> {rxcui, classes}.

    We deliberately return ALL allergy-relevant classes (not just one) because
    auto-picking a single class is unreliable. Example: sulfamethoxazole's CHEM
    classes include BOTH "Sulfamethoxazole" (the drug itself) and "Sulfonamides"
    (the actual class). Phase 4 is where YOU hand-pick the one canonical label.
    """
    rxcui = get_rxcui(drug_name)
    if not rxcui:
        return {"name": drug_name, "rxcui": None, "classes": []}
    classes = [c["class_name"] for c in get_drug_classes(rxcui)]
    return {"name": drug_name, "rxcui": rxcui, "classes": classes}


if __name__ == "__main__":
    test_drugs = ["amoxicillin", "sulfamethoxazole", "ibuprofen", "warfarin", "aspirin"]

    print("3.1 + 3.2 — Drug -> RXCUI -> Allergy-relevant classes (deduped)")
    print("-" * 70)
    for name in test_drugs:
        rxcui = get_rxcui(name)
        if not rxcui:
            print(f"  {name:20s} -> NOT FOUND")
            continue
        class_names = [c["class_name"] for c in get_drug_classes(rxcui)]
        print(f"  {name:20s} -> {rxcui:>6} -> {class_names}")

    print("\n3.3 — resolve_drug_to_class (chained, one call):")
    print("-" * 70)
    for name in test_drugs:
        print(" ", resolve_drug_to_class(name))
