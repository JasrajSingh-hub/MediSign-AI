import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("ocr_service.parser")

class PrescriptionParserService:
    # Common frequency mapping
    FREQUENCY_MAP = {
        r"\b(od|o\.d\.|once daily|once a day)\b": "Once Daily",
        r"\b(bd|bid|b\.i\.d\.|twice daily|twice a day|1-0-1|1-0-0-1)\b": "Twice Daily",
        r"\b(tds|tid|t\.i\.d\.|thrice daily|three times daily|three times a day|1-1-1)\b": "Thrice Daily",
        r"\b(qid|q\.i\.d\.|four times daily|four times a day|1-1-1-1)\b": "Four Times Daily",
        r"\b(hs|h\.s\.|at bedtime|night|at night|0-0-1)\b": "At Bedtime",
        r"\b(prn|p\.r\.n\.|as needed|when required)\b": "As Needed",
        r"\b(1-0-0|once in morning|morning)\b": "Once Daily (Morning)",
        r"\b(0-1-0|once in afternoon|afternoon)\b": "Once Daily (Afternoon)"
    }

    # Common instruction mapping
    INSTRUCTION_MAP = {
        r"\b(ac|a\.c\.|before food|before meal|before meals|empty stomach)\b": "Before Food",
        r"\b(pc|p\.c\.|after food|after meal|after meals)\b": "After Food",
        r"\b(with milk|milk)\b": "With Milk",
        r"\b(with water|water)\b": "With Water"
    }

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parses raw text from a prescription into structured fields.
        """
        logger.info("Parsing raw prescription text...")
        if not text:
            return self._empty_result()

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        result = {
            "doctor_name": "",
            "hospital_name": "",
            "patient_name": "",
            "age": "",
            "gender": "",
            "date": "",
            "medicines": []
        }

        # 1. Parse Metadata
        # Doctor Name Regex
        doc_patterns = [
            r"(?:dr\.|dr\b|doctor)\s*([\w\s\.\u0900-\u097F]+)",  # Supports Unicode/Hindi names
            r"prescribed\s+by\s*[:\-]?\s*([\w\s\.\u0900-\u097F]+)"
        ]
        for line in lines:
            # Check Doctor
            if not result["doctor_name"]:
                for pat in doc_patterns:
                    match = re.search(pat, line, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()
                        # Avoid matching simple words or patient label
                        if len(name) > 2 and not any(k in name.lower() for k in ["patient", "name", "date", "age", "sex"]):
                            result["doctor_name"] = name
                            break

            # Check Patient Name
            if not result["patient_name"]:
                pat_match = re.search(r"\b(?:patient|name|pt|pt\.)\s*(?:name)?\s*[:\-]\s*([\w\s\.\u0900-\u097F]+)", line, re.IGNORECASE)
                if pat_match:
                    pname = pat_match.group(1).strip()
                    if len(pname) > 2 and not any(k in pname.lower() for k in ["doctor", "date", "age", "gender"]):
                        result["patient_name"] = pname

            # Check Hospital Name
            if not result["hospital_name"]:
                hosp_match = re.search(r"([\w\s\.\u0900-\u097F]+(?:hospital|clinic|medical center|health care|nursing home|care center))", line, re.IGNORECASE)
                if hosp_match:
                    result["hospital_name"] = hosp_match.group(1).strip()

            # Check Age
            if not result["age"]:
                # Matches "Age: 45", "45 Yrs", "45 Years", "45/M", "45 Y"
                age_match = re.search(r"\b(?:age|age\s*s)\s*[:\-]?\s*(\d+)\b", line, re.IGNORECASE)
                if age_match:
                    result["age"] = age_match.group(1).strip()
                else:
                    age_match_alt = re.search(r"\b(\d+)\s*(?:yrs|years|yr|y/o|yo)\b", line, re.IGNORECASE)
                    if age_match_alt:
                        result["age"] = age_match_alt.group(1).strip()

            # Check Gender
            if not result["gender"]:
                gender_match = re.search(r"\b(?:gender|sex)\s*[:\-]?\s*(male|female|other|m|f)\b", line, re.IGNORECASE)
                if gender_match:
                    g = gender_match.group(1).strip().lower()
                    if g.startswith('m'):
                        result["gender"] = "Male"
                    elif g.startswith('f'):
                        result["gender"] = "Female"
                    else:
                        result["gender"] = "Other"
                else:
                    # Look for "/M" or "/F" in lines (common pattern: "Age: 45/M")
                    gender_alt = re.search(r"\b\d+\s*/\s*(m|f|male|female)\b", line, re.IGNORECASE)
                    if gender_alt:
                        g = gender_alt.group(1).strip().lower()
                        result["gender"] = "Male" if g.startswith('m') else "Female"

            # Check Date
            if not result["date"]:
                # Common date formats (e.g. DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY)
                date_match = re.search(r"\b(?:date)\s*[:\-]?\s*([\d\-\.\/]+)\b", line, re.IGNORECASE)
                if date_match:
                    result["date"] = date_match.group(1).strip()
                else:
                    date_generic = re.search(r"\b(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})\b", line)
                    if date_generic:
                        result["date"] = date_generic.group(1).strip()

        # 2. Parse Medicines
        # Regex components
        dosage_pattern = r"(\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|tab|caps|cap|tablet|tablets|capsule|capsules|unit|units|u|puff|puffs|drop|drops|tsp|tbsp|%))"
        duration_pattern = r"(?:for\s*)?(\d+\s*(?:day|days|week|weeks|month|months|d|w|m)\b)"

        for line in lines:
            # Skip lines that are purely metadata headers or footer markers
            if any(k in line.lower() for k in ["rx", "prescription", "address", "phone", "tele", "signature", "doctor signature"]):
                # RX is a prefix for prescription, but let's check if the rest of the line has medicine info
                if line.lower().strip() == "rx":
                    continue
            
            # Skip lines matching doctor/hospital/patient details that we already extracted
            if (result["doctor_name"] and result["doctor_name"] in line) or \
               (result["patient_name"] and result["patient_name"] in line) or \
               (result["hospital_name"] and result["hospital_name"] in line):
                # Unless it contains a dosage, in which case it might be a medicine mistakenly grouped
                if not re.search(dosage_pattern, line, re.IGNORECASE):
                    continue

            # Check if this line contains medicine indicators (dosage or frequency symbols)
            has_dosage = re.search(dosage_pattern, line, re.IGNORECASE)
            
            # Check for frequency match
            has_freq = False
            matched_freq_val = ""
            for pat, val in self.FREQUENCY_MAP.items():
                if re.search(pat, line, re.IGNORECASE):
                    has_freq = True
                    matched_freq_val = val
                    break

            # Check for duration match
            dur_match = re.search(duration_pattern, line, re.IGNORECASE)
            matched_dur_val = dur_match.group(1).strip() if dur_match else ""

            # If we have a dosage or frequency, this line is likely a medicine prescription!
            if has_dosage or has_freq or matched_dur_val:
                # Extract dosage
                dose_val = has_dosage.group(1).strip() if has_dosage else ""

                # Extract instructions
                inst_val = ""
                for pat, val in self.INSTRUCTION_MAP.items():
                    if re.search(pat, line, re.IGNORECASE):
                        inst_val = val
                        break

                # Extract medicine name
                # The medicine name is typically everything before the dosage, or everything before the frequency/duration
                # Let's write a parser logic to extract name
                temp_name = line
                
                # Strip Rx if it exists at the start of line
                temp_name = re.sub(r"^[Rr][Xx]\b\s*[:\-]?\s*", "", temp_name)

                # Remove the dosage string from name
                if dose_val:
                    temp_name = temp_name.replace(dose_val, "")
                
                # Remove the duration string from name
                if matched_dur_val:
                    # Remove the matched duration and any preceding "for"
                    temp_name = re.sub(r"\b(?:for\s*)?" + re.escape(matched_dur_val) + r"\b", "", temp_name, flags=re.IGNORECASE)

                # Remove frequency keywords from name
                for pat in self.FREQUENCY_MAP.keys():
                    temp_name = re.sub(pat, "", temp_name, flags=re.IGNORECASE)

                # Remove instruction keywords from name
                for pat in self.INSTRUCTION_MAP.keys():
                    temp_name = re.sub(pat, "", temp_name, flags=re.IGNORECASE)

                # Remove empty parentheses or brackets left behind after removing details
                temp_name = re.sub(r"\(\s*\)", "", temp_name)
                temp_name = re.sub(r"\[\s*\]", "", temp_name)

                # Clean name: remove numbers, leading/trailing punctuation/spaces, bullets
                # Keep alphanumeric words (supporting Unicode characters for Hindi names)
                # Remove bullet prefixes like "1.", "2)", "a.", "-", "*"
                temp_name = re.sub(r"^\s*\d+[\.\)\-]?\s*", "", temp_name)
                temp_name = re.sub(r"^\s*[\-\*\+\u2022]\s*", "", temp_name)
                # Remove punctuation clutter at edges
                temp_name = temp_name.strip(":,.-_ \t\n\r")

                # If name is empty, try to salvage
                if not temp_name and dose_val:
                    # Maybe it's just the dose on this line, but medicine name was on previous line
                    # We can fallback to "Unknown Medicine"
                    temp_name = "Unknown Medicine"

                # Check that name is not a number or purely punctuation
                if temp_name and len(temp_name) > 1 and not re.match(r"^[\d\W_]+$", temp_name):
                    # Clean up multiple spaces
                    temp_name = " ".join(temp_name.split())
                    
                    result["medicines"].append({
                        "name": temp_name,
                        "dose": dose_val,
                        "frequency": matched_freq_val,
                        "duration": matched_dur_val,
                        "instructions": inst_val
                    })

        logger.info(f"Prescription parsed. Extracted {len(result['medicines'])} medicines.")
        return result

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "doctor_name": "",
            "hospital_name": "",
            "patient_name": "",
            "age": "",
            "gender": "",
            "date": "",
            "medicines": []
        }
