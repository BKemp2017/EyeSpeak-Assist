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
# │ Commercial Use: Contact blakekemp01@gmail.com                               │
# └────────────────────────────────────────────────────────────────────────────┘

import cv2

for i in range(3):
    print(f"[INFO] Testing camera index {i}...")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"\n[INFO] Showing live feed from index {i} — Press ESC to close\n")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[INFO] Failed to grab frame.")
                break
            cv2.imshow(f"Camera {i}", frame)
            if cv2.waitKey(1) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print(f"[INFO] Camera index {i} could not be opened.")
