import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_tts/flutter_tts.dart';

import 'blink_detector.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const EyeSpeakApp());
}

class EyeSpeakApp extends StatelessWidget {
  const EyeSpeakApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EyeSpeak Assist Mobile',
      theme: ThemeData.dark(),
      home: const KeyboardScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class KeyboardScreen extends StatefulWidget {
  const KeyboardScreen({super.key});

  @override
  State<KeyboardScreen> createState() => _KeyboardScreenState();
}

class _KeyboardScreenState extends State<KeyboardScreen> {
  final List<List<String>> _layout = [
    'QWERTYUIOP'.split(''),
    'ASDFGHJKL'.split(''),
    'ZXCVBNM./-'.split(''),
  ];

  int _row = 0;
  int _col = 0;
  String _text = '';
  late Timer _timer;
  late FlutterTts _tts;
  BlinkDetector? _detector;
  bool _cooldown = false;

  @override
  void initState() {
    super.initState();
    _tts = FlutterTts();
    _tts.setLanguage("en-US");
    _tts.setSpeechRate(0.5);
    _detector = BlinkDetector(onBlink: _onBlink);
    _timer = Timer.periodic(const Duration(milliseconds: 1500), (timer) {
      setState(() {
        _col++;
        if (_col >= _layout[_row].length) {
          _col = 0;
          _row = (_row + 1) % _layout.length;
        }
      });
    });
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);
  }

  void _onBlink() async {
    if (_cooldown) return;
    _cooldown = true;
    final ch = _layout[_row][_col];
    setState(() {
      if (ch == '-') {
        _tts.stop();
        _tts.speak(_text);
        _text = '';
      } else if (ch == '.') {
        _text += ' ';
      } else if (ch == '/') {
        if (_text.isNotEmpty) {
          _text = _text.substring(0, _text.length - 1);
        }
      } else {
        _text += ch;
      }
    });
    await Future.delayed(const Duration(milliseconds: 800));
    _cooldown = false;
  }

  @override
  void dispose() {
    _timer.cancel();
    _detector?.dispose();
    super.dispose();
  }

  Widget _buildKey(String char, bool highlight) {
    return Container(
      margin: const EdgeInsets.all(4),
      width: 50,
      height: 50,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        border: Border.all(color: highlight ? Colors.green : Colors.white, width: 2),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(char, style: const TextStyle(fontSize: 20)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(_text, style: const TextStyle(fontSize: 24, color: Colors.yellow)),
            ),
            for (int r = 0; r < _layout.length; r++)
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  for (int c = 0; c < _layout[r].length; c++)
                    _buildKey(_layout[r][c], r == _row && c == _col),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
