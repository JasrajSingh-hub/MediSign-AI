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
    patient_id: str
    prescribed_drugs: List[str]
    allergy: AllergyCheckResponse
    interactions: InteractionCheckResponse


class MatchedDrug(BaseModel):
    input_token: str
    matched_drug: str
    confidence: float
    status: str
    brand: str = ""


class OcrAuditResponse(BaseModel):
    patient_id: str
    raw_text: str
    matched_drugs: List[MatchedDrug]
    prescribed_drugs: List[str]
    audit: AuditResponse

