# ┌────────────────────────────────────────────────────────────────────────────┐
# │ EyeSpeak Assist - Blink-Based Communication System                         │
# │ © 2025 Blake Kemp                                                          │
# ├────────────────────────────────────────────────────────────────────────────┤
# │ Licensed under the Creative Commons Attribution-NonCommercial 4.0         │
# │ International License (CC BY-NC 4.0).                                      │
# │                                                                            │
# │ You are free to:                                                           │
# │  • Share — copy and redistribute the material in any medium or format      │
# │  • Adapt — remix, transform, and build upon the material                   │
# │                                                                            │
# │ Under the following terms:                                                 │
# │  • Attribution — You must give appropriate credit and indicate changes     │
# │  • NonCommercial — You may not use the material for commercial purposes    │
# │                                                                            │
# │ License Info: https://creativecommons.org/licenses/by-nc/4.0/              │
# │ Commercial Use: Contact blakekemp01@gmail.com                              │
# └────────────────────────────────────────────────────────────────────────────┘

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None  # Not available on Windows

import cv2

class Camera:
    def __init__(self, width=640, height=480):
        self.using_picamera2 = False

        if Picamera2 is not None:
            try:
                print("[INFO] Attempting to initialize Picamera2")
                self.picam2 = Picamera2()
                config = self.picam2.create_preview_configuration(
                    main={"format": "RGB888", "size": (width, height)}
                )
                self.picam2.configure(config)
                self.picam2.start()
                self.using_picamera2 = True
                print("[INFO] Picamera2 initialized successfully")
            except Exception as e:
                print(f"[INFO] Falling back to OpenCV camera: {e}")

        if not self.using_picamera2:
            print("[INFO] Initializing OpenCV fallback camera")
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            for _ in range(5):
                self.cap.read()

    def get_frame(self):
        if self.using_picamera2:
            return self.picam2.capture_array()
        else:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Failed to capture frame from fallback camera")
                return None
            return frame

    def stop(self):
        if self.using_picamera2:
            self.picam2.stop()
        else:
            self.cap.release()
        cv2.destroyAllWindows()

    def release(self):
        self.stop()
