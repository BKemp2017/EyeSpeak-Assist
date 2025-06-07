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
