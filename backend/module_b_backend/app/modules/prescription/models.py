"""Table definitions for the Module B SQLite DB (offline-first, no ORM needed)."""

CREATE_DRUG_CLASSES = """
CREATE TABLE IF NOT EXISTS drug_allergy_classes (
    ingredient_name TEXT,
    rxcui           TEXT,
    allergy_class   TEXT
)
"""

CREATE_PATIENT_ALLERGIES = """
CREATE TABLE IF NOT EXISTS patient_allergies (
    patient_id    TEXT,
    allergen_class TEXT,
    allergen_text  TEXT,
    severity       TEXT,
    source         TEXT
)
"""

CREATE_DRUG_INTERACTIONS = """
CREATE TABLE IF NOT EXISTS drug_interactions (
    drug_a    TEXT,
    drug_b    TEXT,
    rxcui_a   TEXT,
    rxcui_b   TEXT,
    severity  TEXT,
    description TEXT,
    mechanism TEXT,
    source    TEXT
)
"""

CREATE_DRUG_ALTERNATIVES = """
CREATE TABLE IF NOT EXISTS drug_alternatives (
    avoid_class       TEXT,
    alternative_drug   TEXT,
    alternative_class  TEXT,
    indication         TEXT,
    note               TEXT,
    source             TEXT
)
"""

CREATE_BRAND_NAMES = """
CREATE TABLE IF NOT EXISTS brand_names (
    brand_name    TEXT,
    generic_name  TEXT
)
"""

CREATE_MEDICINE_KNOWLEDGE = """
CREATE TABLE IF NOT EXISTS medicine_knowledge (
    generic_name       TEXT PRIMARY KEY,
    drug_class         TEXT,
    therapeutic_class  TEXT,
    common_indications TEXT,
    body_system        TEXT,
    common_symptoms    TEXT,
    red_flag_symptoms  TEXT
)
"""

CREATE_REASONING_CACHE = """
CREATE TABLE IF NOT EXISTS reasoning_cache (
    signature           TEXT PRIMARY KEY,
    domain_signature    TEXT,
    medicines_json      TEXT,
    contexts_json       TEXT,
    question_categories TEXT,
    question_tree_json  TEXT,
    red_flags_json      TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
