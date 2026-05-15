from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import shutil
import os
import cv2
import numpy as np
import ast
import json

from deepface import DeepFace

from database import get_db
from ai.liveness import LivenessDetector
from ai.ocr_utils import verify_ocr

app = FastAPI(title="SafeBankID - Secure Identity System")

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

liveness_detector = LivenessDetector()


# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/")
def health():
    return {"status": "SafeBankID Online"}


# ----------------------------
# STEP 1 - ADD USER
# ----------------------------
@app.post("/add-user")
def add_user(
    name: str = Form(...),
    id_number: str = Form(...),
    dob: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        db.execute(text("""
            INSERT INTO users (name, id_number, dob)
            VALUES (:n, :id, :d)
            ON CONFLICT (id_number)
            DO UPDATE SET name=:n, dob=:d
        """), {"n": name, "id": id_number, "d": dob})

        db.commit()

        return {
            "success": True,
            "user_id": id_number
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# STEP 2 - OCR + STORE FACE EMBEDDING
# ----------------------------
@app.post("/verify-id")
async def verify_id(
    full_name: str = Form(...),
    id_number: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    expiry_date: str = Form(...),
    id_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        contents = await id_file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        # OCR
        user_data = {
            "full_name": full_name,
            "id_number": id_number,
            "dob": dob,
            "gender": gender,
            "expiry_date": expiry_date
        }

        report = verify_ocr(img, user_data)
        print("OCR REPORT:", report) 

        if report["status"] != "verified":
            return {
                "success": False,
                "step": "ocr_failed",
                "ocr_result": report
            }

        # Save temp image
        temp_path = f"temp_{id_number}.jpg"
        cv2.imwrite(temp_path, img)

        # Face embedding
        embedding = DeepFace.represent(
            img_path=temp_path,
            model_name="VGG-Face",
            enforce_detection=True
        )[0]["embedding"]

        os.remove(temp_path)

        # Store embedding
        embedding_json = json.dumps(embedding)
        db.execute(text("""
            INSERT INTO face_embeddings (user_id, embedding)
            VALUES (:uid, cast(:emb as jsonb))
            ON CONFLICT (user_id)
            DO UPDATE SET embedding=cast(:emb as jsonb)
        """), {
            "uid": id_number,
            "emb": embedding_json
        })
      

        db.commit()

        return {
            "success": True,
            "step": "id_verified",
            "ocr_result": report
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ----------------------------
# STEP 3 - LIVE FACE VERIFY
# ----------------------------
@app.post("/verify-secure/{user_id}")
async def verify_secure(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    temp_path = f"live_{user_id}.jpg"

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # ---------------- LOAD EMBEDDING ----------------
        row = db.execute(text("""
            SELECT embedding FROM face_embeddings WHERE user_id=:uid
        """), {"uid": user_id}).fetchone()

        if not row:
            return {
                "success": False,
                "access": "DENIED",
                "reason": "No stored face found"
            }

        # FIX: safer conversion
        stored_embedding = np.array(row[0], dtype=np.float32)

        # ---------------- LIVE EMBEDDING ----------------
        live_embedding = DeepFace.represent(
            img_path=temp_path,
            model_name="VGG-Face",
            enforce_detection=True
        )[0]["embedding"]

        live_embedding = np.array(live_embedding, dtype=np.float32)

        # ---------------- SIMILARITY ----------------
        similarity = float(
            np.dot(live_embedding, stored_embedding) /
            (np.linalg.norm(live_embedding) * np.linalg.norm(stored_embedding))
        )

        # ✅ FIX 1: lower threshold
        face_match = bool(similarity > 0.50)

        # ---------------- LIVENESS ----------------
        liveness = liveness_detector.check_liveness(temp_path)
        is_alive = bool(liveness.get("is_alive", False))
        liveness_score = float(liveness.get("liveness_score", 0))

        # ✅ FIX 2: smarter decision (IMPORTANT)
        final_score = (similarity * 0.7) + (liveness_score * 0.3)
        final = final_score > 0.60

        return {
            "success": True,
            "access": "GRANTED" if final else "DENIED",
            "confidence": similarity,
            "liveness_score": liveness_score,
            "final_score": final_score,
            "face_match": face_match,
            "is_alive": is_alive
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)