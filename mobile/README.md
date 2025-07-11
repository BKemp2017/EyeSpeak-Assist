# EyeSpeak Assist Mobile

This directory contains a simplified Flutter implementation of **EyeSpeak Assist** for Android and iOS. It provides a scanning on‑screen keyboard and uses blink detection to select keys.

The project depends on Google's ML Kit for blink detection and the platform text‑to‑speech engine.

## Building

1. Install Flutter (>=3.10) and the Android/iOS SDKs.
2. Run `flutter pub get` inside this `mobile` directory.
3. Connect a device or start an emulator.
4. Run `flutter run` to launch the app.

A release build can be generated with `flutter build apk` or `flutter build ios`.

## Compliance Notes

- The camera feed is processed only for real‑time blink detection and is not stored.
- A camera usage description must be provided in the Android manifest and iOS `Info.plist` when publishing to the stores.
- Audio is generated using the native text‑to‑speech services (`FlutterTts`).

This mobile code is provided under the same **CC BY‑NC 4.0** license as the desktop version.
