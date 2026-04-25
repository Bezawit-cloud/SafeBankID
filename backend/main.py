from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from ai.face_verification import FaceVerifier
from ai.liveness import LivenessDetector
import shutil
import os

app = FastAPI()

# Initialize AI Tools
verifier = FaceVerifier()
liveness_detector = LivenessDetector()

@app.get("/")
def check_status():
    return {"status": "SafeBankID System Online"}

@app.post("/add-user")
def add_user(name: str, email: str, dob: str, db: Session = Depends(get_db)):
    query = text("INSERT INTO users (name, email, dob) VALUES (:n, :e, :d)")
    db.execute(query, {"n": name, "e": email, "d": dob})
    db.commit()
    return {"message": f"Successfully added {name} to SafeBankID"}

@app.post("/verify-secure/{user_id}")
async def verify_secure(user_id: str, file: UploadFile = File(...)):
    # 1. Save File
    temp_path = f"temp_{user_id}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Run Both AI Checks
    identity = verifier.verify(temp_path, user_id)
    liveness = liveness_detector.check_liveness(temp_path)

    # 3. Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # 4. Final Security Decision
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
        "reason": "Identity Match Failure" if not is_verified else "Spoofing/Fake Photo Detected",
        "details": {"identity": is_verified, "liveness": is_alive}
    }