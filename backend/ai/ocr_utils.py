import re
import cv2
import pytesseract
from rapidfuzz import fuzz

def extract_id_fields(img: np.ndarray) -> dict:
    processed = preprocess_for_id(img)
    # Use PSM 6 (Assume a single uniform block of text) for better line-by-line reading
    raw_text = pytesseract.image_to_string(processed, config='--psm 6')
    raw_text = normalize_months(raw_text)
    
    extracted = {
        "full_name": None,
        "dob": None,
        "id_number": None
    }

    # 1. Extract Name (Look for line after "Full Name")
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    for i, line in enumerate(lines):
        if "FULL NAME" in line.upper() and i + 1 < len(lines):
            extracted["full_name"] = lines[i+1]
            break

    # 2. Extract DOB (Look for text after "Date of Birth" or "የትውልድ ቀን")
    dob_match = re.search(r"(?:Date of Birth|የትውልድ ቀን).*?([\d/]{8,15})", raw_text, re.IGNORECASE)
    if dob_match:
        extracted["dob"] = dob_match.group(1).split('|')[0].strip()

    # 3. Extract FAN (ID Number) - Look specifically for "FAN" label
    fan_match = re.search(r"FAN\D*(\d{12,18})", raw_text, re.IGNORECASE)
    if fan_match:
        extracted["id_number"] = fan_match.group(1).strip()

    return extracted

def verify_ocr(img: np.ndarray, user_input: dict) -> dict:
    extracted = extract_id_fields(img)
    
    # Fuzzy Name Match
    name_score = fuzz.token_sort_ratio(
        user_input.get("full_name", "").upper(),
        (extracted["full_name"] or "").upper()
    )
    
    # Exact ID Match (cleaned of non-digits)
    ext_id = re.sub(r'\D', '', extracted.get("id_number") or "")
    inp_id = re.sub(r'\D', '', user_input.get("id_number") or "")
    id_score = 100 if (ext_id and ext_id == inp_id) else 0
    
    # DOB Match (partial match to handle format differences)
    ext_dob = extracted.get("dob") or ""
    inp_dob = user_input.get("dob", "").replace("-", "/")
    dob_score = 100 if inp_dob in ext_dob or ext_dob in inp_dob else 0

    return {
        "status": "verified" if (id_score == 100 and name_score > 70) else "failed",
        "match_scores": {"full_name": name_score, "id_number": id_score, "dob": dob_score},
        "extracted_data": extracted
    }