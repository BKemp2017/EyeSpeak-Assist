# modules/speech_engine.py
import subprocess

class SpeechEngine:
    def say(self, text):
        try:
            subprocess.run(["espeak", "-s", "140", "-p", "70", text], check=True)
        except Exception as e:
            print(f"[ERROR] Failed to speak: {e}")
