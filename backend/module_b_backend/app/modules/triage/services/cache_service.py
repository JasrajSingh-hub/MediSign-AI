"""Phase 3 & 4: Two-Tier Reasoning Cache Service.

Generates exact medicine signature hashes and therapeutic domain hashes to check
and store reasoning results in SQLite, maximizing offline cache hits.
"""
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple
from module_b_backend.app.modules.triage import repository


def generate_exact_signature(drugs: List[str], emergency_sign: Optional[str] = None) -> str:
    """Generate SHA256 signature hash from emergency sign and sorted lowercase drug names."""
    clean_drugs = sorted([d.strip().lower() for d in drugs if d.strip()])
    raw_str = f"sign:{emergency_sign.upper() if emergency_sign else 'NONE'}|drugs:" + "|".join(clean_drugs)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


def generate_domain_signature(therapeutic_domains: List[str], emergency_sign: Optional[str] = None) -> str:
    """Generate SHA256 domain signature hash from emergency sign and sorted therapeutic domains."""
    clean_domains = sorted([t.strip().lower() for t in therapeutic_domains if t.strip()])
    raw_str = f"sign:{emergency_sign.upper() if emergency_sign else 'NONE'}|domains:" + "|".join(clean_domains)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


def lookup_reasoning_cache(
    drugs: List[str], therapeutic_domains: List[str], emergency_sign: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]], str, str]:
    """Check Tier 1 (exact signature) and Tier 2 (domain signature) cache.

    Returns:
        (cache_hit, cache_type, cache_entry_dict, signature, domain_signature)
    """
    signature = generate_exact_signature(drugs, emergency_sign)
    domain_signature = generate_domain_signature(therapeutic_domains, emergency_sign)

    # Tier 1: Exact Medicine + Sign Signature Hit
    exact_hit = repository.get_reasoning_cache_by_signature(signature)
    if exact_hit:
        return True, "exact_hit", exact_hit, signature, domain_signature

    # Tier 2: Domain + Sign Signature Hit
    domain_hit = repository.get_reasoning_cache_by_domain_signature(domain_signature)
    if domain_hit:
        return True, "domain_hit", domain_hit, signature, domain_signature

    return False, "llm_miss", None, signature, domain_signature


def save_to_cache(
    signature: str,
    domain_signature: str,
    drugs: List[str],
    contexts: List[str],
    question_categories: List[str],
    question_tree: List[Dict[str, Any]],
    red_flags: List[str],
) -> None:
    """Save newly generated reasoning result into SQLite for permanent offline reuse."""
    repository.save_reasoning_cache(
        signature=signature,
        domain_signature=domain_signature,
        medicines=drugs,
        contexts=contexts,
        question_categories=question_categories,
        question_tree=question_tree,
        red_flags=red_flags,
    )
