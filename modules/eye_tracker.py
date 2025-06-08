# eye_tracker.py
import time
import cv2
import mediapipe as mp
from collections import deque

class EyeTracker:
    def __init__(self, camera_index=0, cap=None):
        print("[INFO] Attempting to initialize webcam...")
        self.cap = cap if cap is not None else cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("[INFO] Could not open webcam.")
        print("[INFO] Webcam initialized.")

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.left_lid_top = 159
        self.left_lid_bottom = 145
        self.right_lid_top = 386
        self.right_lid_bottom = 374

        self.last_blink_time = 0
        self.blink_cooldown = 0.5  # seconds

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None, None, False, None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        blink = False

        if not results.multi_face_landmarks:
            return frame, None, False, None

        face = results.multi_face_landmarks[0]
        ih, iw, _ = frame.shape

        def pt(index):
            lm = face.landmark[index]
            return int(lm.x * iw), int(lm.y * ih)

        try:
            top_lid_l, bottom_lid_l = pt(self.left_lid_top), pt(self.left_lid_bottom)
            top_lid_r, bottom_lid_r = pt(self.right_lid_top), pt(self.right_lid_bottom)

            height_l = abs(bottom_lid_l[1] - top_lid_l[1])
            height_r = abs(bottom_lid_r[1] - top_lid_r[1])

            current_time = time.time()
            if (height_l < 5 or height_r < 5) and (current_time - self.last_blink_time > self.blink_cooldown):
                blink = True
                self.last_blink_time = current_time

        except Exception as e:
            print(f"[INFO] Blink detection error: {e}")

        return frame, None, blink, None

    def release(self):
        self.cap.release()
