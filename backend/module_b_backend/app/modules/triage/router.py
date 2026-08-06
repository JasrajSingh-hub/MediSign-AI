"""FastAPI router for Triage Engine and Reasoning Cache endpoints."""
from fastapi import APIRouter

from module_b_backend.app.modules.triage.schemas import (
    QuestionItem,
    TriageContextRequest,
    TriageContextResponse,
    TriageSummaryRequest,
    TriageSummaryResponse,
)
from module_b_backend.app.modules.triage.services import (
    cache_service,
    context_builder,
    llm_triage_generator,
    rule_engine,
    summary_service,
)

router = APIRouter(prefix="/triage", tags=["triage"])


@router.post("/context", response_model=TriageContextResponse)
def get_triage_context(req: TriageContextRequest):
    """Retrieve or generate clinical triage contexts, question trees, and red flags."""
    if req.emergency_sign and req.emergency_sign.upper() == "AMBULANCE":
        return TriageContextResponse(
            patient_id=req.patient_id,
            instant_critical=True,
            cache_hit=True,
            cache_type="instant_emergency",
            signature="critical_ambulance",
            domain_signature="critical_ambulance",
            contexts=["Critical Emergency"],
            question_categories=["Immediate Staff Call"],
            red_flags=["Ambulance Sign Detected"],
            question_tree=[],
        )

    clinical_ctx = context_builder.build_clinical_context(req.drugs)

    cache_hit, cache_type, cache_data, signature, domain_signature = cache_service.lookup_reasoning_cache(
        req.drugs, clinical_ctx["therapeutic_domains"], req.emergency_sign
    )

    instant_critical = False
    if cache_hit and cache_data:
        contexts = cache_data["contexts"]
        question_categories = cache_data["question_categories"]
        red_flags = cache_data["red_flags"]
        question_tree_raw = cache_data["question_tree"]
    else:
        # Cache MISS -> Call LLM generator & persist to cache
        gen_data = llm_triage_generator.generate_triage_context_llm(
            req.drugs, clinical_ctx, signature, domain_signature, req.emergency_sign
        )
        instant_critical = gen_data.get("instant_critical", False)
        contexts = gen_data.get("contexts", [])
        question_categories = gen_data.get("question_categories", [])
        red_flags = gen_data.get("red_flags", [])
        question_tree_raw = gen_data.get("question_tree", [])

    question_tree = [QuestionItem(**q) for q in question_tree_raw]

    return TriageContextResponse(
        patient_id=req.patient_id,
        instant_critical=instant_critical,
        cache_hit=cache_hit,
        cache_type=cache_type,
        signature=signature,
        domain_signature=domain_signature,
        contexts=contexts,
        question_categories=question_categories,
        red_flags=red_flags,
        question_tree=question_tree,
    )


@router.post("/summary", response_model=TriageSummaryResponse)
def get_triage_summary(req: TriageSummaryRequest):
    """Evaluate patient answers via Rule Engine and generate clinician handoff summary."""
    clinical_ctx = context_builder.build_clinical_context(req.drugs)
    known_red_flags = clinical_ctx.get("aggregated_red_flags", [])

    priority, red_flag_alert, triggered_red_flags = rule_engine.evaluate_triage_priority(
        req.answers, known_red_flags
    )

    doctor_summary = summary_service.generate_doctor_summary(
        patient_id=req.patient_id,
        drugs=req.drugs,
        context=req.context or "General Consultation",
        answers=req.answers,
        priority=priority,
        red_flag_alert=red_flag_alert,
        triggered_red_flags=triggered_red_flags,
    )

    return TriageSummaryResponse(
        patient_id=req.patient_id,
        priority=priority,
        red_flag_alert=red_flag_alert,
        triggered_red_flags=triggered_red_flags,
        doctor_summary=doctor_summary,
    )
