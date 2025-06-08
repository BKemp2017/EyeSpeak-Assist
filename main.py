import cv2
import time
import pygame
import pyautogui
import os
import numpy as np
from modules.eye_tracker import EyeTracker
from modules.speech_engine import SpeechEngine
from ui.interface import EyeSpeakInterface

import pyautogui

def show_splash_screen():
    splash = cv2.imread("assets/images/splash.png")
    if splash is None:
        print("[WARNING] Splash image not found.")
        return

    # Get actual screen resolution using pyautogui
    screen_width, screen_height = pyautogui.size()

    splash = cv2.resize(splash, (screen_width, screen_height))
    window_name = "EyeSpeak Splash"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Fade in
    for alpha in range(0, 101, 5):
        overlay = splash.copy()
        output = cv2.addWeighted(overlay, alpha / 100.0, splash, 0, 0)
        cv2.imshow(window_name, output)
        cv2.waitKey(30)

    # Hold for 5 second
    cv2.imshow(window_name, splash)
    cv2.waitKey(5000)

    # Fade out
    for alpha in range(100, -1, -5):
        overlay = splash.copy()
        output = cv2.addWeighted(overlay, alpha / 100.0, splash, 0, 0)
        cv2.imshow(window_name, output)
        cv2.waitKey(30)

    cv2.destroyWindow(window_name)

def wait_for_camera():
    window_name = "Initializing EyeSpeak"
    width, height = 800, 200
    bar_length = 600
    bar_height = 40
    max_wait_time = 5  # seconds
    start_time = time.time()
    camera_ready = False
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else 0)  # DSHOW helps avoid freezing on Windows

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, width, height)
    cv2.moveWindow(window_name, 300, 300)  # Adjust as needed to center on screen

    progress = 0

    while time.time() - start_time < max_wait_time:
        elapsed = time.time() - start_time
        progress = int((elapsed / max_wait_time) * bar_length)

        screen = 255 * np.ones((height, width, 3), dtype=np.uint8)
        cv2.putText(screen, "Initializing Camera...", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2)
        cv2.rectangle(screen, (100, 120), (100 + bar_length, 120 + bar_height), (220, 220, 220), -1)
        cv2.rectangle(screen, (100, 120), (100 + progress, 120 + bar_height), (0, 255, 0), -1)

        cv2.imshow(window_name, screen)
        key = cv2.waitKey(50)
        if key == 27:  # ESC to exit
            print("[INFO] User cancelled camera init.")
            cap.release()
            cv2.destroyWindow(window_name)
            return False

        if not camera_ready and cap.isOpened():
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                camera_ready = True
                break

    if not camera_ready:
        cap.release()
        print("[ERROR] Camera initialization failed.")
        cv2.destroyWindow(window_name)
        return None

    for p in range(progress, bar_length + 1, 10):
        screen = 255 * np.ones((height, width, 3), dtype=np.uint8)
        cv2.putText(screen, "Camera Ready!", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2)
        cv2.rectangle(screen, (100, 120), (100 + bar_length, 120 + bar_height), (220, 220, 220), -1)
        cv2.rectangle(screen, (100, 120), (100 + p, 120 + bar_height), (0, 255, 0), -1)
        cv2.imshow(window_name, screen)
        if cv2.waitKey(20) == 27:
            print("[INFO] User cancelled during final animation.")
            cv2.destroyWindow(window_name)
            return None
    cv2.waitKey(500)
    cv2.destroyWindow(window_name)
    return cap

def main():
    show_splash_screen()
    cap = wait_for_camera()
    if cap is None:
        return

    tracker = EyeTracker(cap=cap)
    speech = SpeechEngine()
    ui = EyeSpeakInterface()
    pygame.init()
    try: 
        pygame.mixer.init()
        select_sound = pygame.mixer.Sound("assets/sounds/boop-3.wav")
    except pygame.error:
        print("[ERROR] Audio not available - continuing without sound")
        select_sound = None

    # # Setup fullscreen window once before the loop
    cv2.namedWindow("EyeSpeak Interface", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("EyeSpeak Interface", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        last_update = time.time()
        interval = 0.86

        while True:
            frame, _, blink, _ = tracker.get_frame()
            if frame is None:
                continue
            current_time = time.time()

            if current_time - last_update > interval:
                if not ui.selection_mode:
                    if not ui.just_spoke_phrase:
                        ui.advance_key()
                else:
                    ui.toggle_confirmation()
                last_update = current_time

            if blink:
                if select_sound:
                    select_sound.play()
                result = ui.blink_triggered()
                if result == "ENTER":
                    sentence = ui.text_buffer.strip()
                    if sentence:
                        print(f"[INFO] Speaking: {sentence}")
                        speech.say(sentence)
                        ui.text_buffer = ""
                elif result:
                    print(f"[INFO] Speaking Phrase: {result}")
                    speech.say(result)

            frame = ui.draw_ui(frame)

            cv2.imshow("EyeSpeak Interface", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                break
            if cv2.getWindowProperty("EyeSpeak Interface", cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        tracker.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
