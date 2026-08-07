from fastapi import APIRouter, File, Form, UploadFile

from .schemas import (
    AllergyCheckRequest,
    AllergyCheckResponse,
    AlternativeSuggestion,
    AuditResponse,
    InteractionCheckRequest,
    InteractionCheckResponse,
    InteractionItem,
    MatchedDrug,
    OcrAuditResponse,
)
from . import repository
from .services import (
    allergy_checker,
    drug_matcher,
    interaction_checker,
    ocr_service,
    vision_ocr_service,
)

router = APIRouter(prefix="/api/v1/prescription", tags=["prescription"])


@router.post("/allergy-check", response_model=AllergyCheckResponse)
def allergy_check(req: AllergyCheckRequest):
    result = allergy_checker.check_allergies(req.patient_id, req.prescribed_drugs)
    conflicts = [
        {
            "drug": c["drug"],
            "matched_class": c["matched_class"],
            "allergy_class": c["allergy_class"],
            "alternatives": [
                AlternativeSuggestion(
                    alternative_drug=a["alternative_drug"],
                    alternative_class=a["alternative_class"],
                    indication=a["indication"],
                    note=a["note"],
                )
                for a in c.get("alternatives", [])
            ],
        }
        for c in result["conflicts"]
    ]
    return AllergyCheckResponse(patient_id=result["patient_id"], conflicts=conflicts, safe=result["safe"])


@router.post("/interaction-check", response_model=InteractionCheckResponse)
def interaction_check(req: InteractionCheckRequest):
    result = interaction_checker.check_interactions(req.patient_id, req.prescribed_drugs)
    interactions = [
        InteractionItem(
            drug_a=i["drug_a"],
            drug_b=i["drug_b"],
            severity=i["severity"],
            description=i["description"],
            mechanism=i["mechanism"],
        )
        for i in result["interactions"]
    ]
    return InteractionCheckResponse(patient_id=result["patient_id"], interactions=interactions, safe=result["safe"])


@router.post("/audit", response_model=AuditResponse)
def audit(req: AllergyCheckRequest):
    allergy_resp = allergy_check(req)
    interaction_resp = interaction_check(req)
    return AuditResponse(
        patient_id=req.patient_id,
        prescribed_drugs=req.prescribed_drugs,
        allergy=allergy_resp,
        interactions=interaction_resp,
    )


@router.post("/ocr-audit", response_model=OcrAuditResponse)
async def ocr_audit(patient_id: str = Form("P001"), image: UploadFile = File(...)):
    image_bytes = await image.read()
    extracted_drugs, ocr_source = vision_ocr_service.extract_drugs(image_bytes)

    if ocr_source != "fallback" and extracted_drugs:
        for d in extracted_drugs:
            name = d.get("name", "").strip()
            brand = d.get("brand", "").strip()
            d_class = d.get("drug_class", "").strip()
            if brand and name and brand.lower() != name.lower():
                repository.add_brand_mapping(brand, name)
            if name and d_class:
                repository.add_drug_class(name, d_class)

        vision_names = [d["name"] for d in extracted_drugs if d.get("name")]
        synthetic_text = "\n".join(vision_names)
        matched, _tokens = drug_matcher.match_drugs(synthetic_text)

        matched_names = {m["matched_drug"].lower() for m in matched}
        for d in extracted_drugs:
            g_name = d.get("name", "").strip()
            if g_name and g_name.lower() not in matched_names:
                matched.append({
                    "matched_drug": g_name,
                    "input_token": d.get("brand") or g_name,
                    "confidence": 95.0,
                    "status": "auto_learned",
                    "brand": d.get("brand", ""),
                })

        raw_text_lines = []
        for d in extracted_drugs:
            line = d["name"]
            if d.get("brand") and d["brand"] != d["name"]:
                line += f"  (brand: {d['brand']})"
            if d.get("drug_class"):
                line += f"  [{d['drug_class']}]"
            if d.get("dosage"):
                line += f"  {d['dosage']}"
            if d.get("frequency"):
                line += f"  ({d['frequency']})"
            raw_text_lines.append(line)
        raw_text = "\n".join(raw_text_lines)
    else:
        raw_text = ocr_service.extract_text(image_bytes)
        matched, _tokens = drug_matcher.match_drugs(raw_text)
        ocr_source = "tesseract"

    drug_names = [m["matched_drug"] for m in matched]
    audit_resp = audit(AllergyCheckRequest(patient_id=patient_id, prescribed_drugs=drug_names))
    return OcrAuditResponse(
        patient_id=patient_id,
        raw_text=f"[{ocr_source.upper()}]\n{raw_text}",
        matched_drugs=[MatchedDrug(**m) for m in matched],
        prescribed_drugs=drug_names,
        audit=audit_resp,
    )
