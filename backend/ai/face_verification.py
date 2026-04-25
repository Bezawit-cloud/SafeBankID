import os
from deepface import DeepFace

class FaceVerifier:
    def __init__(self, reference_folder="uploaded_faces"):
        # We go up one level from the 'ai' folder to find 'uploaded_faces'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.reference_folder = os.path.join(base_dir, reference_folder)
        
        if not os.path.exists(self.reference_folder):
            os.makedirs(self.reference_folder)

    def verify(self, live_image_path: str, user_id: str):
        # Ensure path uses the user_id correctly
        reference_path = os.path.join(self.reference_folder, f"{user_id}.jpg")

        if not os.path.exists(reference_path):
            return {"error": f"Reference photo not found at {reference_path}"}

        try:
            # DeepFace.verify handles the heavy lifting
            result = DeepFace.verify(
                img1_path = live_image_path,
                img2_path = reference_path,
                model_name = "VGG-Face",
                distance_metric = "cosine",
                enforce_detection = True,
                detector_backend = "opencv" # Options: 'opencv', 'retinaface', 'mtcnn'
            )

            return {
                "verified": bool(result["verified"]),
                "confidence": round(1 - result["distance"], 4),
                "status": "Match" if result["verified"] else "Mismatch"
            }
        except Exception as e:
            # If no face is detected, DeepFace throws an exception
            return {"error": f"AI Processing Error: {str(e)}"}