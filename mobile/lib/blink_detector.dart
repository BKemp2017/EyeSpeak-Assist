import "dart:ui" show Size;
import 'dart:async';
import 'package:camera/camera.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';

/// Simple blink detector using ML Kit face detection.
/// Calls [onBlink] whenever both eyes are closed for more than 0.5s.
class BlinkDetector {
  final void Function() onBlink;
  late final FaceDetector _detector;
  CameraController? _controller;
  bool _processing = false;
  DateTime _lastBlink = DateTime.now();

  BlinkDetector({required this.onBlink}) {
    _detector = FaceDetector(options: const FaceDetectorOptions());
    _initialize();
  }

  Future<void> _initialize() async {
    final cams = await availableCameras();
    if (cams.isEmpty) return;
    _controller = CameraController(cams.first, ResolutionPreset.medium);
    await _controller!.initialize();
    await _controller!.startImageStream(_processImage);
  }

  Future<void> _processImage(CameraImage image) async {
    if (_processing) return;
    _processing = true;
    try {
      final inputImage = _toInputImage(image, _controller!);
      final faces = await _detector.processImage(inputImage);
      if (faces.isNotEmpty) {
        final f = faces.first;
        final left = f.leftEyeOpenProbability ?? 1.0;
        final right = f.rightEyeOpenProbability ?? 1.0;
        if (left < 0.4 && right < 0.4) {
          if (DateTime.now().difference(_lastBlink).inMilliseconds > 500) {
            _lastBlink = DateTime.now();
            onBlink();
          }
        }
      }
    } catch (_) {} finally {
      _processing = false;
    }
  }

  InputImage _toInputImage(CameraImage image, CameraController controller) {
    final format = InputImageFormatValue.fromRawValue(image.format.raw) ?? InputImageFormat.nv21;
    return InputImage.fromBytes(
      bytes: image.planes[0].bytes,
      inputImageData: InputImageData(
        size: Size(controller.value.previewSize!.height, controller.value.previewSize!.width),
        imageRotation: InputImageRotationValue.fromRawValue(controller.description.sensorOrientation) ?? InputImageRotation.rotation0deg,
        inputImageFormat: format,
        planeData: image.planes.map(
          (p) => InputImagePlaneMetadata(bytesPerRow: p.bytesPerRow, height: p.height, width: p.width),
        ).toList(),
      ),
    );
  }

  void dispose() {
    _controller?.dispose();
    _detector.close();
  }
}
