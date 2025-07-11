# EyeSpeak Assist Mobile

This directory contains a simplified Flutter implementation of **EyeSpeak Assist** for Android and iOS. It provides a scanning on‑screen keyboard and uses blink detection to select keys.

The project depends on Google's ML Kit for blink detection and the platform text‑to‑speech engine.

## Building

1. Install Flutter (>=3.10) and the Android/iOS SDKs.
2. Run `flutter pub get` inside this `mobile` directory.
3. Connect a device or start an emulator.
4. Run `flutter run` to launch the app.

A release build can be generated with `flutter build apk` or `flutter build ios`.

## Using a Samsung S25 Ultra for Testing

1. Enable developer options on the phone:
   - Open **Settings** → **About phone** → **Software information**.
   - Tap **Build number** seven times to unlock developer options.
2. Return to **Settings** → **Developer options** and enable **USB debugging**.
3. Install the Samsung USB drivers on your computer (or Android File Transfer on macOS).
4. Connect the phone to your computer with a USB cable and confirm the debugging prompt on the device.
5. Run `flutter devices` to verify that the S25 Ultra appears in the device list.
6. Execute `flutter run` from this directory to build and launch the app on the phone.

## Compliance Notes

- The camera feed is processed only for real‑time blink detection and is not stored.
- A camera usage description must be provided in the Android manifest and iOS `Info.plist` when publishing to the stores.
- Audio is generated using the native text‑to‑speech services (`FlutterTts`).

This mobile code is provided under the same **CC BY‑NC 4.0** license as the desktop version.
