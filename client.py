import cv2
import requests
import numpy as np

def start_demo():
    # 1. Ask for the User ID before starting the camera
    user_id = input("Enter User ID to verify (e.g., 1, 2, 3): ").strip()
    if not user_id:
        print("User ID is required!")
        return

    # Dynamically build the URL based on input
    API_URL = f"http://127.0.0.1:8000/verify-secure/{user_id}"
    
    cap = cv2.VideoCapture(0)
    print(f"Webcam Active for User {user_id}. Press SPACE to Login, Q to Quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = frame.copy()
        cv2.putText(display_frame, f"SafeBankID: User {user_id}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Live Demo", display_frame)

        key = cv2.waitKey(1)
        
        # SPACE key to trigger verification
        if key == ord(' '):
            print("Verifying...")
            
            # Convert frame to image in memory (faster than saving to disk)
            _, img_encoded = cv2.imencode('.jpg', frame)
            files = {"file": ("live.jpg", img_encoded.tobytes(), "image/jpeg")}
            
            try:
                r = requests.post(API_URL, files=files)
                res = r.json()
                
                # Check results
                access_status = res.get("access", "DENIED")
                reason = res.get("reason", "Unknown error")
                
                # Visual feedback
                color = (0, 255, 0) if access_status == "GRANTED" else (0, 0, 255)
                cv2.putText(display_frame, access_status, (100, 200), 
                            cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)
                
                if access_status == "DENIED":
                    print(f"Access Denied: {reason}")
                else:
                    print("Access Granted!")

                cv2.imshow("Live Demo", display_frame)
                cv2.waitKey(2000) # Show result for 2 seconds
                
            except Exception as e:
                print(f"Connection Error: {e}")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_demo()