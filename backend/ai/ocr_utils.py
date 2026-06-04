import re
import cv2
import numpy as np
import pytesseract
from rapidfuzz import fuzz

# -------- CONFIGURATION --------
TESSERACT_CMD = "/usr/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# -------- HELPER: FIX OCR MONTH ERRORS --------
def normalize_months(text):
    corrections = {
        "DUL": "JUL", "IUL": "JUL", "JUI": "JUL",
        "JUL": "JUL", "JAN": "JAN", "FEB": "FEB",
        "MAR": "MAR", "APR": "APR", "MAY": "MAY",
        "JUN": "JUN", "AUG": "AUG", "SEP": "SEP",
        "OCT": "OCT", "NOV": "NOV", "DEC": "DEC"
    }
    text = text.upper()
    for wrong, correct in corrections.items():
        text = re.sub(wrong, correct, text)
    return text


# -------- ✅ NEW: NORMALIZE DOB TO YYYY-MM-DD --------
def normalize_dob(dob_str: str) -> str:
    if not dob_str:
        return ""
    dob_str = dob_str.strip()

    # Already YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', dob_str):
        return dob_str

    # DD/MM/YYYY → YYYY-MM-DD
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', dob_str)
    if m:
        return f"{m.group(3)}-{m.group(1)}-{m.group(2)}"

    # YYYY/MM/DD → YYYY-MM-DD
    m = re.match(r'^(\d{4})/(\d{2})/(\d{2})$', dob_str)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # MM/DD/YYYY → YYYY-MM-DD
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', dob_str)
    if m:
        return f"{m.group(3)}-{m.group(1)}-{m.group(2)}"

    # YYYY/MON/DD e.g. 2033/AUG/20
    months = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }
    m = re.match(r'^(\d{4})/([A-Z]{3})/(\d{2})$', dob_str.upper())
    if m and m.group(2) in months:
        return f"{m.group(1)}-{months[m.group(2)]}-{m.group(3)}"

    # DD-MON-YYYY e.g. 20-AUG-2033
    m = re.match(r'^(\d{2})-([A-Z]{3})-(\d{4})$', dob_str.upper())
    if m and m.group(2) in months:
        return f"{m.group(3)}-{months[m.group(2)]}-{m.group(1)}"

    return dob_str


# -------- IMAGE PREPROCESSING --------
def preprocess_for_id(img: np.ndarray) -> np.ndarray:
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


# -------- OCR EXTRACTION --------
def extract_id_fields(img: np.ndarray) -> dict:
    processed = preprocess_for_id(img)

    text_psm3 = pytesseract.image_to_string(processed, config='--oem 3 --psm 3')
    text_psm11 = pytesseract.image_to_string(processed, config='--oem 3 --psm 11')
    text_numbers = pytesseract.image_to_string(
        processed,
        config='--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    )

    combined_raw = text_psm3 + "\n" + text_psm11 + "\n" + text_numbers
    combined_raw = normalize_months(combined_raw)

    lines = [l.strip() for l in combined_raw.split('\n') if len(l.strip()) > 2]

    extracted = {
        "full_name": None,
        "dob": None,
        "id_number": None,
        "gender": None,
        "expiry": None,
        "_candidates": []
    }

    # 1. NAME EXTRACTION
    blacklist = ["NATIONAL", "IDENTITY", "CARD", "REPUBLIC", "FEDERAL",
                 "OFFICE", "RESIDENT", "FULL", "NAME", "ETHIOPIAN"]

    for line in lines:
        if not any(w in line.upper() for w in blacklist) and not any(c.isdigit() for c in line):
            if 2 <= len(line.split()) <= 5:
                extracted["_candidates"].append(line.strip())

    if extracted["_candidates"]:
        extracted["full_name"] = max(extracted["_candidates"], key=len)

    # 2. DATE EXTRACTION
    dates = re.findall(
        r'(\d{2}/\d{2}/\d{4}|\d{4}/[A-Z]{3}/\d{2}|\d{4}/\d{2}/\d{2}|\d{2}-\d{2}-\d{4})',
        combined_raw
    )
    if dates:
        unique_dates = sorted(list(set(dates)))
        extracted["dob"] = unique_dates[0]
        extracted["expiry"] = unique_dates[-1]

    # 3. ID NUMBER EXTRACTION
    for line in lines:
        if "ID" in line.upper():
            nums = re.findall(r'\d{12,18}', line)
            if nums:
                extracted["id_number"] = nums[0]
                break

    if not extracted["id_number"]:
        chunks = re.findall(r'\d+', combined_raw)
        candidates = [c for c in chunks if 12 <= len(c) <= 18]
        if candidates:
            extracted["id_number"] = min(candidates, key=lambda x: abs(len(x) - 16))

    if not extracted["id_number"]:
        all_digits = re.sub(r'\D', '', combined_raw)
        possible_ids = []
        for i in range(len(all_digits) - 15):
            segment = all_digits[i:i+16]
            possible_ids.append(segment)
        if possible_ids:
            extracted["id_number"] = possible_ids[-1]

    # 4. GENDER
    if re.search(r'\b(FEMALE|WOMAN)\b', combined_raw):
        extracted["gender"] = "Female"
    elif re.search(r'\b(MALE|MAN)\b', combined_raw):
        extracted["gender"] = "Male"

    return extracted


# -------- ✅ UPDATED VERIFICATION --------
def verify_ocr(img: np.ndarray, user_input: dict) -> dict:
    extracted = extract_id_fields(img)

    # ✅ Name match — use both algorithms, take the best score
    name_score = max(
        fuzz.token_sort_ratio(
            user_input.get("full_name", "").upper(),
            (extracted["full_name"] or "").upper()
        ),
        fuzz.token_set_ratio(
            user_input.get("full_name", "").upper(),
            (extracted["full_name"] or "").upper()
        )
    )

    # ✅ DOB match — normalize both sides to YYYY-MM-DD first
    input_dob     = normalize_dob(user_input.get("dob", ""))
    extracted_dob = normalize_dob(extracted["dob"] or "")
    dob_match = 0
    if input_dob and extracted_dob:
        if input_dob == extracted_dob:
            dob_match = 100
        elif fuzz.ratio(input_dob, extracted_dob) > 75:
            dob_match = 80

    # ✅ ID match — strip spaces and dashes before comparing
    id_score     = 0
    input_id     = re.sub(r'[\s\-]', '', user_input.get("id_number", ""))
    extracted_id = re.sub(r'[\s\-]', '', extracted["id_number"] or "")
    if input_id and extracted_id:
        if input_id == extracted_id:
            id_score = 100
        elif input_id in extracted_id or extracted_id in input_id:
            id_score = 90
        elif fuzz.ratio(input_id, extracted_id) > 85:
            id_score = 80

    match_scores = {
        "full_name": name_score,
        "id_number": id_score,
        "dob": dob_match
    }

    # ✅ Pass if name matches + either ID or DOB matches
    is_verified = name_score > 65 and (id_score >= 80 or dob_match >= 80)

    return {
        "status": "verified" if is_verified else "failed",
        "match_scores": match_scores,
        "extracted_data": extracted,
        "reason": None if is_verified else "Name, ID or DOB did not match"
    }