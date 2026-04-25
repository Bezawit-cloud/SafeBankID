import cv2
import numpy as np
import importlib.util
import os
import mediapipe

# 1. Locate the physical folder where mediapipe is installed
mp_base_path = os.path.dirname(mediapipe.__file__)
# 2. Construct the direct path to the face_mesh file
# On Windows, this is usually: ...\mediapipe\python\solutions\face_mesh.py
target_path = os.path.join(mp_base_path, 'python', 'solutions', 'face_mesh.py')

# 3. Use importlib to "force" the import from that path
spec = importlib.util.spec_from_file_location("mp_face_mesh", target_path)
mp_face_mesh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp_face_mesh)

class LivenessDetector:
    def __init__(self):
        # Now we use the forced module
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True, 
            max_num_faces=1,
            refine_landmarks=True
        )

    def get_blur_score(self, image):
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def check_liveness(self, image_path):
        frame = cv2.imread(image_path)
        if frame is None:
            return {"liveness_score": 0, "is_alive": False}

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_score = self.get_blur_score(gray)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return {"liveness_score": 0, "is_alive": False, "status": "No Face Detected"}

        liveness_score = 0.0
        if blur_score > 100:
            liveness_score += 0.6
        liveness_score += 0.3 

        return {
            "liveness_score": round(liveness_score, 2),
            "is_alive": liveness_score >= 0.8,
            "blur_metric": round(blur_score, 2)
        }