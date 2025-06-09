# 🧠 EyeSpeak — Blink-Driven Speech for ALS Users

EyeSpeak Assist is an accessible, Raspberry Pi–ready, blink-based speech interface designed for individuals with ALS and other motor impairments. It uses a webcam to detect blinks and enables the user to select letters and phrases from a custom onscreen keyboard — hands-free, voice-powered communication.

---

## 🚀 Features

- ✅ **Blink-Based Selection**: Navigate and select keys by blinking — no mouse or hands required.
- ✅ **Onscreen Keyboard UI**: Automatically highlights one key at a time.
- ✅ **Smart key prediction** using dictionary-based filtering  
- ✅ **YES/NO Confirmation**: Prevents accidental keypresses.
- ✅ **Custom Phrase Panel**: Easily add/edit phrases via a YAML file (`ui/phrases.yml`).
- ✅ **Text-to-Speech Output**: Speaks selected phrases using `espeak`.
- ✅ **Raspberry Pi Compatible**: Optimized for low-resource devices.
- ✅ **Camera Auto-Detection**: Supports multiple webcam indexes.

---

## 🧠 How It Works

- The app cycles through keys on a custom keyboard UI.
- The user **blinks** to select a highlighted key.
- A **YES/NO prompt** confirms the input to avoid mistakes.
- When the **"PHRASES"** key is selected, a panel of prewritten phrases appears.
- On confirmation, the selected text or phrase is **spoken aloud** using `espeak`.

---

## 📸 Screenshots

### Full Keyboard with Scanning Cursor
![Screenshot 2025-06-07 013546](https://github.com/user-attachments/assets/bded13f0-7915-4bc2-a398-ea1b37592b03)

### Phrase Panel View
![Screenshot 2025-06-07 013617](https://github.com/user-attachments/assets/b9efcbb2-a0ec-4cfb-a23c-136873dbeec6)

### Example Message Composed
![Screenshot 2025-06-07 013720](https://github.com/user-attachments/assets/118b8c41-b24e-4c4c-a463-ec2c5942a944)
- **Live word prediction:**  
  As the user spells a word, only letters that continue a valid word (from a dictionary) remain enabled — dramatically improving typing speed and reducing error

### Confirmation Prompt to avoid accidental key-presses
![image](https://github.com/user-attachments/assets/c6c28c45-a35c-4075-b08f-6e56ca39157d)

---

## 📦 Installation

### 1. Clone the Repo

```bash
git clone https://github.com/YOUR_USERNAME/eye_speak_assist.git
cd eye_speak_assist
```

### 2. Create a Virtual Environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/macOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install opencv-python mediapipe numpy pygame pyautogui pyyaml
sudo apt install espeak
```

If you don’t have a `requirements.txt`, manually install:

```bash
pip install opencv-python mediapipe numpy pyyaml
```

> ⚠️ On Windows, also install [`espeak`](http://espeak.sourceforge.net/download.html) and ensure it's added to your PATH.

---

## 🧪 Testing Your Camera

If `main.py` fails to detect your webcam, try:

```python
# test_camera_index.py
import cv2

for i in range(3):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"Camera {i} works!")
        cap.release()
```

---

## ▶️ Run the App

```bash
python main.py
```

---

## 🛠 Customize

### 🔡 Add Custom Phrases

Edit `ui/phrases.yml`:

```yaml
- phrase: "I'm thirsty"
- phrase: "Turn on the TV"
- phrase: "Thank you"
```

### 📖 Add a Dictionary (Optional)

For future word prediction:

```python
# interface.py
path = r"C:\Users\blake\american-english"  # or /usr/share/dict/american-english
```

---

## 📷 Compatible Hardware

- Raspberry Pi 5 (tested)
- Logitech webcams (e.g., C925-E)
- 8MP Pi camera module (onboard)
- Windows or Ubuntu (VM or physical)

---

## ❤️ Credits

- Gaze & blink detection: [MediaPipe](https://google.github.io/mediapipe/)
- Text-to-speech: `espeak`
- Dev environment: Python 3.12, OpenCV, YAML
- Project by [Blake Kemp]

---

## 📘 License

This project is open-source under the MIT License.
