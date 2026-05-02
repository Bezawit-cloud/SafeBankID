from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import shutil
import os
import cv2
import numpy as np

# Internal Imports
from database import get_db
from ai.face_verification import FaceVerifier
from ai.liveness import LivenessDetector
from ai.ocr_utils import verify_ocr  # Updated to the advanced logic

app = FastAPI(title="SafeBankID - Secure Identity System")

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Tools
verifier = FaceVerifier()
liveness_detector = LivenessDetector()

@app.get("/")
def check_status():
    return {"status": "SafeBankID System Online"}

# --- USER MANAGEMENT ---

@app.post("/add-user")
def add_user(name: str, email: str, dob: str, db: Session = Depends(get_db)):
    query = text("INSERT INTO users (name, email, dob) VALUES (:n, :e, :d)")
    db.execute(query, {"n": name, "e": email, "d": dob})
    db.commit()
    return {"message": f"Successfully added {name} to SafeBankID"}

# --- BIOMETRIC CHECK (Face + Liveness) ---

@app.post("/verify-secure/{user_id}")
async def verify_secure(user_id: str, file: UploadFile = File(...)):
    temp_path = f"temp_{user_id}_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        identity = verifier.verify(temp_path, user_id)
        liveness = liveness_detector.check_liveness(temp_path)

        is_verified = identity.get("verified", False)
        is_alive = liveness.get("is_alive", False)

        if is_verified and is_alive:
            return {
                "access": "GRANTED",
                "user_id": user_id,
                "confidence": identity["confidence"],
                "liveness_score": liveness["liveness_score"]
            }
        
        return {
            "access": "DENIED",
            "reason": "Identity Match Failure" if not is_verified else "Spoofing Detected",
            "details": {"identity": is_verified, "liveness": is_alive}
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# --- ID CARD CHECK (Advanced OCR) ---

@app.post("/verify-id")
async def verify_id(
    full_name: str = Form(...), 
    id_number: str = Form(...),
    dob: str = Form(...),            # Added to match advanced logic
    gender: str = Form(...),         # Added to match advanced logic
    expiry_date: str = Form(...),    # Added to match advanced logic
    id_file: UploadFile = File(...)
):
    # 1. Convert upload to OpenCV format
    contents = await id_file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # 2. Bundle User Data for Comparison
    user_data = {
        "full_name": full_name,
        "id_number": id_number,
        "dob": dob,
        "gender": gender,
        "expiry_date": expiry_date
    }

    # 3. Run the Advanced OCR Verification Logic
    # This calls the verify_ocr function from your ocr_utils.py
    report = verify_ocr(img, user_data)
    
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)