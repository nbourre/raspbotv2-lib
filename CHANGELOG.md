# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---



## [0.1.2] - 2026-04-07
### Changed
- Fixed motor direction logic for diagonal movements.

## [0.1.1] - 2026-04-07
### Changed
- Improved documentation and examples.

## [0.1.0] - 2026-04-07

### Added

- Initial public release.
- `Robot` facade providing unified access to all hardware subsystems.
- `Motors` -- differential drive with forward/backward/left/right/stop helpers and
  mecanum wheel extensions (strafe, diagonal moves).
- `Servo` / `ServoPair` -- single and paired servo control with angle clamping.
- `Buzzer` -- non-blocking beep and pattern scheduling via cooperative `update(ct)`.
- `LedBar` -- per-LED and all-LED colour/brightness control.
- `LightEffects` -- five animated effects (river, breathing, random_running, starlight,
  gradient) driven by a non-blocking `update(ct)` state machine.
- `UltrasonicSensor` -- distance reading in mm and cm.
- `LineTracker` -- 4-channel IR line sensor.
- `IRReceiver` -- IR remote keycode reading.
- `Button` -- on-board push button.
- `OLEDDisplay` -- SSD1306 OLED via luma.oled (optional extra).
- `Camera` -- OpenCV camera capture (optional extra).
- `Task` -- cooperative rate-gate utility mirroring the Arduino `millis()` pattern.
- Full MkDocs documentation site (Material theme).
- 15 runnable examples covering every subsystem.
- PEP 561 typed package (`py.typed` marker).
- MIT licence.

[0.1.0]: https://github.com/nbourre/raspbotv2-lib/releases/tag/v0.1.0
