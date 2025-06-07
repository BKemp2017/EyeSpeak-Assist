import cv2
import time
from modules.eye_tracker import EyeTracker
from modules.speech_engine import SpeechEngine
from ui.interface import EyeSpeakInterface

def main():
    tracker = EyeTracker(camera_index=0)
    speech = SpeechEngine()
    ui = EyeSpeakInterface()

    # Setup fullscreen window once before the loop
    cv2.namedWindow("EyeSpeak Interface", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("EyeSpeak Interface", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        last_update = time.time()
        interval = 0.86

        while True:
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
            if blink:
                cv2.putText(frame, "[INFO] Blink Detected", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 255), 2)

            cv2.imshow("EyeSpeak Interface", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                break
    finally:
        tracker.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
