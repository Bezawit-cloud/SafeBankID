import numpy as np
from deepface import DeepFace
from sqlalchemy import text

class FaceVerifier:

    # -----------------------------
    # 🔥 GET EMBEDDING
    # -----------------------------
    def get_embedding(self, img_path):
        try:
            embedding = DeepFace.represent(
                img_path=img_path,
                model_name="VGG-Face",
                enforce_detection=False
            )

            return np.array(embedding[0]["embedding"])

        except Exception as e:
            raise Exception(f"Embedding failed: {str(e)}")

    # -----------------------------
    # 🔥 COSINE SIMILARITY
    # -----------------------------
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # -----------------------------
    # 🔥 NEW VERIFY (DB BASED)
    # -----------------------------
    def verify(self, live_image_path: str, user_id: str, db):
        try:
            # 1️⃣ Get stored embedding from DB
            result = db.execute(
                text("SELECT embedding FROM face_embeddings WHERE user_id = :uid"),
                {"uid": user_id}
            ).fetchone()

            if not result:
                return {"error": "No stored face found for this user"}

            stored_embedding = np.array(result[0])

            # 2️⃣ Get live embedding
            live_embedding = self.get_embedding(live_image_path)

            # 3️⃣ Compare
            similarity = self.cosine_similarity(stored_embedding, live_embedding)

            # 🔥 threshold (tune this)
            threshold = 0.6

            verified = similarity > threshold

            return {
                "verified": verified,
                "confidence": round(float(similarity), 4),
                "status": "Match" if verified else "Mismatch"
            }

        except Exception as e:
            return {"error": str(e)}