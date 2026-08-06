from pathlib import Path
import sqlite3

BACKEND_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND_DIR / "data" / "rxnorm_local.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS drug_allergy_classes (
                ingredient_name TEXT PRIMARY KEY,
                allergy_class TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS patient_allergies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                allergen_class TEXT NOT NULL,
                allergen_text TEXT NOT NULL,
                severity TEXT DEFAULT 'unknown',
                source TEXT DEFAULT 'curated'
            );

            CREATE TABLE IF NOT EXISTS drug_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_a TEXT NOT NULL,
                drug_b TEXT NOT NULL,
                rxcui_a TEXT DEFAULT '',
                rxcui_b TEXT DEFAULT '',
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                mechanism TEXT DEFAULT '',
                source TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS drug_alternatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                avoid_class TEXT NOT NULL,
                alternative_drug TEXT NOT NULL,
                alternative_class TEXT NOT NULL,
                indication TEXT NOT NULL,
                note TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS brand_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL,
                generic_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS medicine_knowledge (
                generic_name       TEXT PRIMARY KEY,
                drug_class         TEXT,
                therapeutic_class  TEXT,
                common_indications TEXT,
                body_system        TEXT,
                common_symptoms    TEXT,
                red_flag_symptoms  TEXT
            );

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
            );
            """
        )
        conn.commit()

    finally:
        conn.close()


def seed_database() -> None:
    conn = get_connection()
    try:
        conn.executescript(
            """
            INSERT OR IGNORE INTO drug_allergy_classes (ingredient_name, allergy_class) VALUES
                ('amoxicillin', 'penicillin'),
                ('ampicillin', 'penicillin'),
                ('cefuroxime', 'cephalosporin'),
                ('azithromycin', 'macrolide'),
                ('ibuprofen', 'nsaid'),
                ('diclofenac', 'nsaid'),
                ('acetaminophen', 'analgesic'),
                ('cetirizine', 'antihistamine'),
                ('aspirin', 'nsaid'),
                ('warfarin', 'anticoagulant');

            INSERT OR IGNORE INTO patient_allergies (patient_id, allergen_class, allergen_text, severity, source) VALUES
                ('P001', 'penicillin', 'penicillin allergy', 'high', 'seed'),
                ('P001', 'nsaid', 'nsaid allergy', 'medium', 'seed'),
                ('P002', 'macrolide', 'macrolide allergy', 'medium', 'seed'),
                ('P_demo_safe', 'sulfonamide', 'demo safe patient allergy', 'low', 'demo'),
                ('P_demo_warn', 'penicillin', 'demo allergy trigger', 'high', 'demo');

            INSERT OR IGNORE INTO drug_interactions (drug_a, drug_b, rxcui_a, rxcui_b, severity, description, mechanism, source) VALUES
                ('warfarin', 'aspirin', '', '', 'MAJOR', 'Increased bleeding risk when combined.', 'platelet inhibition plus anticoagulation', 'seed'),
                ('lisinopril', 'ibuprofen', '', '', 'MODERATE', 'NSAIDs can reduce antihypertensive effect.', 'renal prostaglandin effect', 'seed'),
                ('metformin', 'contrast media', '', '', 'MAJOR', 'Risk of lactic acidosis in susceptible patients.', 'renal function impairment', 'seed'),
                ('amoxicillin', 'warfarin', '', '', 'MODERATE', 'May increase anticoagulant effect in some patients.', 'gut flora / vitamin k effect', 'demo'),
                ('aspirin', 'warfarin', '', '', 'MAJOR', 'Higher bleeding risk with combined use.', 'dual anticoagulant effect', 'demo');

            INSERT OR IGNORE INTO drug_alternatives (avoid_class, alternative_drug, alternative_class, indication, note) VALUES
                ('penicillin', 'azithromycin', 'macrolide', 'bacterial infection', 'Use only if clinically appropriate'),
                ('nsaid', 'acetaminophen', 'analgesic', 'pain or fever', 'Preferred when NSAIDs are contraindicated'),
                ('macrolide', 'doxycycline', 'tetracycline', 'respiratory infection', 'Review patient-specific contraindications'),
                ('penicillin', 'cefuroxime', 'cephalosporin', 'bacterial infection', 'Demo alternative suggestion'),
                ('nsaid', 'paracetamol', 'analgesic', 'pain or fever', 'Demo alternative suggestion');

            INSERT OR IGNORE INTO brand_names (brand_name, generic_name) VALUES
                ('amoxil', 'amoxicillin'),
                ('augmentin', 'amoxicillin'),
                ('napa', 'acetaminophen'),
                ('tylenol', 'acetaminophen'),
                ('brufen', 'ibuprofen'),
                ('advil', 'ibuprofen'),
                ('ecosprin', 'aspirin'),
                ('dolo', 'acetaminophen'),
                ('dolo 650', 'acetaminophen'),
                ('augmentin 625', 'amoxicillin');
            """
        )
        conn.commit()
    finally:
        conn.close()


def ensure_database_ready() -> None:
    initialize_database()
    seed_database()
