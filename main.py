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
# │ Commercial Use: Contact blake@yourdomain.com                               │
# └────────────────────────────────────────────────────────────────────────────┘


import cv2
import time
import pygame
import pyautogui
import os
import numpy as np
from modules.eye_tracker import EyeTracker
from modules.speech_engine import SpeechEngine
from modules.camera import Camera  
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
    from modules.camera import Camera

    window_name = "Initializing EyeSpeak"
    width, height = 800, 200
    bar_length = 600
    bar_height = 40
    max_wait_time = 5  # seconds
    start_time = time.time()
    camera_ready = False
    camera = None

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, width, height)
    cv2.moveWindow(window_name, 300, 300)

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
        if key == 27:
            print("[INFO] User cancelled camera init.")
            cv2.destroyWindow(window_name)
            return None

        if not camera_ready:
            try:
                print("[DEBUG] Trying to initialize camera...")
                camera = Camera()
                frame = camera.get_frame()
                if frame is not None:
                    camera_ready = True
                    break
                else:
                    print("[DEBUG] Camera.get_frame() returned None.")
            except Exception as e:
                print(f"[ERROR] Exception while initializing camera: {e}")
                camera = None

    if not camera_ready:
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
    return camera

def main():
    show_splash_screen()
    camera = wait_for_camera()
    if camera is None:
        return

    tracker = EyeTracker(camera=camera)
    speech = SpeechEngine()
    ui = EyeSpeakInterface()
    pygame.init()
    try: 
        pygame.mixer.init()
        select_sound = pygame.mixer.Sound("assets/sounds/boop-3.wav")
    except pygame.error:
        print("[ERROR] Audio not available - continuing without sound")
        select_sound = None

    screen_w, screen_h = pyautogui.size()    

    cv2.namedWindow("EyeSpeak Interface", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("EyeSpeak Interface", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        last_update = time.time()
        interval = 0.86

        while True:
            frame = camera.get_frame()
            if frame is None:
                continue

            frame, _, blink, _ = tracker.get_frame()
            
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
            frame = cv2.resize(frame, (screen_w, screen_h))
        
            cv2.imshow("EyeSpeak Interface", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                break
            if cv2.getWindowProperty("EyeSpeak Interface", cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        camera.stop()
        tracker.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
