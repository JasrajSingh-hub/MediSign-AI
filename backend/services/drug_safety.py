import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("ocr_service.safety")

class DrugSafetyService:
    def check_safety(self, parsed_data: Dict[str, Any], ocr_confidence: float) -> List[str]:
        """
        Runs medication safety checks on the parsed prescription data.
        Returns a list of warning strings.
        """
        logger.info("Executing drug safety checks...")
        warnings = []

        # 1. Check Overall OCR Confidence
        if ocr_confidence < 0.50:
            warnings.append(f"Low overall OCR confidence score ({ocr_confidence:.2f}). Please verify all details manually.")

        medicines = parsed_data.get("medicines", [])
        
        # Track seen medicine names to detect duplicates
        seen_medicines = {}
        
        for idx, med in enumerate(medicines):
            name = med.get("name", "").strip()
            dose = med.get("dose", "").strip()
            freq = med.get("frequency", "").strip()
            
            # Skip if name is invalid/placeholder
            if not name:
                warnings.append(f"Medicine #{idx+1} has an empty or unreadable name.")
                continue
                
            if name == "Unknown Medicine":
                warnings.append(f"Medicine #{idx+1} could not be successfully read. Please verify.")
                continue

            # 2. Check for Duplicate Medicines (Case-insensitive check)
            name_key = " ".join(name.lower().split())
            if name_key in seen_medicines:
                warnings.append(f"Duplicate medication detected: '{name}'. First match found at line {seen_medicines[name_key]+1}.")
            else:
                seen_medicines[name_key] = idx

            # 3. Check for Missing Dosage
            if not dose:
                warnings.append(f"Dosage missing for medication: '{name}'.")

            # 4. Check for Missing Frequency
            if not freq:
                warnings.append(f"Frequency details missing for medication: '{name}'.")

            # 5. Check for Suspicious OCR spelling (e.g. alphanumeric corruption like 'Pa1acetam0l' or 'Ib_profen')
            # Common pattern is digits or unusual symbols mixed inside alphabetic drug names.
            # We ignore trailing digits that could be part of drug variants (e.g., 'Amoxicillin 2', 'Paracetamol 650') 
            # by checking if digits are surrounded by letters.
            if re.search(r"[a-zA-Z]\d[a-zA-Z]", name) or re.search(r"[@#\$%\^&\*\(\)_\+\|~=\{\}\[\]:;<>?/]", name):
                warnings.append(f"Suspicious characters detected in medication name: '{name}'. Possible OCR misspelling.")

        logger.info(f"Drug safety check complete. Generated {len(warnings)} warnings.")
        return warnings
