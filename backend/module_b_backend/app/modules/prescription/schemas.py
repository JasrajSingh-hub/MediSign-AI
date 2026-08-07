"""Pydantic request/response models for the prescription API."""
from typing import List
from pydantic import BaseModel


class AllergyCheckRequest(BaseModel):
    patient_id: str
    prescribed_drugs: List[str]


class AlternativeSuggestion(BaseModel):
    alternative_drug: str
    alternative_class: str
    indication: str
    note: str = ""


class ConflictItem(BaseModel):
    drug: str
    matched_class: str
    allergy_class: str
    alternatives: List[AlternativeSuggestion] = []


class AllergyCheckResponse(BaseModel):
    patient_id: str
    conflicts: List[ConflictItem]
    safe: List[dict]


class InteractionItem(BaseModel):
    drug_a: str
    drug_b: str
    severity: str
    description: str
    mechanism: str = ""


class InteractionCheckRequest(BaseModel):
    patient_id: str
    prescribed_drugs: List[str]


class InteractionCheckResponse(BaseModel):
    patient_id: str
    interactions: List[InteractionItem]
    safe: List[str]


class AuditResponse(BaseModel):
    """Single combined response for one prescription (the merged endpoint).

    Wraps the allergy and interaction check results so the Flutter app makes one
    call instead of two. Reuses both sub-feature response shapes unchanged.
    """
    patient_id: str
    prescribed_drugs: List[str]
    allergy: AllergyCheckResponse
    interactions: InteractionCheckResponse


class MatchedDrug(BaseModel):
    input_token: str
    matched_drug: str    # always the generic name
    confidence: float
    status: str          # 'confident' | 'unverified'
    brand: str = ""      # brand read from the image, or "" if generic was used


class OcrAuditResponse(BaseModel):
    """Response for the scan pipeline: OCR -> drug match -> full audit.

    Lets the test UI photograph a printed prescription and see everything the
    backend derived from it in one call.
    """
    patient_id: str
    raw_text: str
    matched_drugs: List[MatchedDrug]
    prescribed_drugs: List[str]
    audit: AuditResponse
