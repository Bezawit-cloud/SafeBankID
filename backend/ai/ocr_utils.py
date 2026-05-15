import re
import cv2
import numpy as np
import pytesseract
from rapidfuzz import fuzz

# -------- CONFIGURATION --------
# TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
TESSERACT_CMD = "/usr/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# -------- HELPER: FIX OCR MONTH ERRORS --------
def normalize_months(text):
    corrections = {
        "DUL": "JUL",
        "IUL": "JUL",
        "JUI": "JUL",
        "JUL": "JUL",
        "JAN": "JAN",
        "FEB": "FEB",
        "MAR": "MAR",
        "APR": "APR",
        "MAY": "MAY",
        "JUN": "JUN",
        "AUG": "AUG",
        "SEP": "SEP",
        "OCT": "OCT",
        "NOV": "NOV",
        "DEC": "DEC"
    }

    text = text.upper()
    for wrong, correct in corrections.items():
        text = re.sub(wrong, correct, text)

    return text


# -------- IMAGE PREPROCESSING --------
def preprocess_for_id(img: np.ndarray) -> np.ndarray:
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


# -------- OCR EXTRACTION --------
def extract_id_fields(img: np.ndarray) -> dict:
    processed = preprocess_for_id(img)

    # Multi-mode OCR
    text_psm3 = pytesseract.image_to_string(processed, config='--oem 3 --psm 3')
    text_psm11 = pytesseract.image_to_string(processed, config='--oem 3 --psm 11')

    # Numeric-focused OCR
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

    # -------- 1. NAME EXTRACTION --------
    blacklist = ["NATIONAL", "IDENTITY", "CARD", "REPUBLIC", "FEDERAL", "OFFICE", "RESIDENT", "FULL", "NAME"]

    for line in lines:
        if not any(w in line.upper() for w in blacklist) and not any(c.isdigit() for c in line):
            if 2 <= len(line.split()) <= 5:
                extracted["_candidates"].append(line.strip())

    if extracted["_candidates"]:
        extracted["full_name"] = max(extracted["_candidates"], key=len)

    # -------- 2. DATE EXTRACTION --------
    dates = re.findall(
        r'(\d{2}/\d{2}/\d{4}|\d{4}/[A-Z]{3}/\d{2}|\d{4}/\d{2}/\d{2}|\d{2}-\d{2}-\d{4})',
        combined_raw
    )

    if dates:
        unique_dates = sorted(list(set(dates)))
        extracted["dob"] = unique_dates[0]
        extracted["expiry"] = unique_dates[-1]

    # -------- 3. SMART ID EXTRACTION --------

    # Step 1: Look for ID near keyword (HIGH PRIORITY)
    for line in lines:
        if "ID" in line.upper():
            nums = re.findall(r'\d{12,18}', line)
            if nums:
                extracted["id_number"] = nums[0]
                break

    # Step 2: If not found, use chunk filtering
    if not extracted["id_number"]:
        chunks = re.findall(r'\d+', combined_raw)
        candidates = [c for c in chunks if 12 <= len(c) <= 18]

        if candidates:
            # pick closest to 16 digits
            extracted["id_number"] = min(candidates, key=lambda x: abs(len(x) - 16))

    # Step 3: Final fallback (sliding window)
    if not extracted["id_number"]:
        all_digits = re.sub(r'\D', '', combined_raw)

        possible_ids = []
        for i in range(len(all_digits) - 15):
            segment = all_digits[i:i+16]
            possible_ids.append(segment)

        if possible_ids:
            extracted["id_number"] = possible_ids[-1]

    # -------- 4. GENDER --------
    if re.search(r'\b(FEMALE|WOMAN)\b', combined_raw):
        extracted["gender"] = "Female"
    elif re.search(r'\b(MALE|MAN)\b', combined_raw):
        extracted["gender"] = "Male"

    return extracted


# -------- VERIFICATION --------
def verify_ocr(img: np.ndarray, user_input: dict) -> dict:
    extracted = extract_id_fields(img)

    # Name match
    name_score = fuzz.token_sort_ratio(
        user_input.get("full_name", "").upper(),
        (extracted["full_name"] or "").upper()
    )

    # DOB match
    input_dob = user_input.get("dob", "").replace("//", "/").upper()
    dob_match = 0

    if extracted["dob"]:
        extracted_dob = extracted["dob"].upper()
        if input_dob in extracted_dob or fuzz.ratio(input_dob, extracted_dob) > 85:
            dob_match = 100

    # ID match (robust)
    id_score = 0
    if user_input.get("id_number") and extracted["id_number"]:
        if user_input["id_number"] in extracted["id_number"]:
            id_score = 100

    match_scores = {
        "full_name": name_score,
        "id_number": id_score,
        "dob": dob_match
    }

    is_verified = (id_score == 100 and name_score > 80)

    return {
        "status": "verified" if is_verified else "failed",
        "match_scores": match_scores,
        "extracted_data": extracted
    }