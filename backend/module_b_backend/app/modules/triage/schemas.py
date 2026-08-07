"""Pydantic schemas for the Triage Engine and Reasoning Cache."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class TriageContextRequest(BaseModel):
    patient_id: str = "P001"
    drugs: List[str] = []
    emergency_sign: Optional[str] = None  # e.g., 'AMBULANCE', 'HEART', 'BREATHING', 'KNEE', 'HELP'


class QuestionItem(BaseModel):
    id: str
    category: str
    question: str
    type: str = "choice"  # 'choice' or 'boolean'
    options: List[str] = ["Yes", "No"]
    follow_up: Optional[Dict[str, Any]] = None


class TriageContextResponse(BaseModel):
    patient_id: str
    instant_critical: bool = False  # True for AMBULANCE (no questions needed)
    cache_hit: bool
    cache_type: str  # 'exact_hit', 'domain_hit', or 'llm_miss'
    signature: str
    domain_signature: str
    contexts: List[str]
    question_categories: List[str]
    red_flags: List[str]
    question_tree: List[QuestionItem]


class TriageSummaryRequest(BaseModel):
    patient_id: str = "P001"
    drugs: List[str] = []
    emergency_sign: Optional[str] = None
    context: Optional[str] = "General Health Inquiry"
    answers: Dict[str, str] = {}  # e.g., {"symptom": "Pain", "duration": "1 Day"}


class TriageSummaryResponse(BaseModel):
    patient_id: str
    priority: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    red_flag_alert: bool
    triggered_red_flags: List[str] = []
    doctor_summary: str
