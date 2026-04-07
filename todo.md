# TODO - Build and Publish Independent Raspbot/OLED Python Library

# Goal
I have access to these libraries which are not maintained and have issues with dependencies and hardware coupling:
- `Raspbot_Lib` (for motor control, sensors, etc.)
- `yahboom_oled` (for OLED display control)

I want to create a new Python package that provides a clean, well-designed API for controlling the Raspbot hardware and OLED display, without relying on these existing libraries. This will allow me to maintain the codebase more easily, add features, and ensure compatibility with future Raspberry Pi OS updates.

I want to publish this package on PyPI so that it can be easily installed and used by others in the Raspberry Pi community. The package should be modular, well-documented, and include tests to ensure reliability.



## 1. Define Scope and Strategy
- [x] Decide the package name (PyPI + import name) → **`raspbot`**
- [x] Define supported hardware/features for v1:
  - [x] Motor control → `raspbot.actuators.motors`
  - [x] Servo control → `raspbot.actuators.servo`
  - [x] Ultrasonic distance → `raspbot.sensors.ultrasonic`
  - [x] OLED text rendering → `raspbot.display.oled`
  - [x] Line tracker → `raspbot.sensors.line_tracker`
  - [x] Button input → `raspbot.sensors.button` (KEY1, register 0x0D)
  - [x] Buzzer control → `raspbot.actuators.buzzer`
  - [x] RGB light bar control → `raspbot.actuators.led_bar`
  - [x] IR sensor input → `raspbot.sensors.ir`
  - [x] Camera capture (OpenCV-compatible) → `raspbot.camera.opencv_camera` (optional extra `[camera]`)
- [x] Decide minimum Python version → **3.10+**
- [x] Define Raspberry Pi OS/hardware targets → Pi with I2C bus 1, address 0x2B
- [x] Decide whether OLED support is bundled or an optional extra → **optional extra `[oled]`**
- [x] Decide whether camera/OpenCV support is bundled or provided as an optional extra → **optional extra `[camera]`**

## 2. Remove Dependency on Existing Raspbot Library
- [x] Inventory every `Raspbot_Lib` call currently used in scripts
- [x] Create an API mapping document → see migration table in README.md
- [x] Re-implement low-level communication in your own module → `src/raspbot/bus.py` (I2C via `smbus2`)
- [x] Validate register addresses and data formats from hardware docs
- [x] Add robust error handling for I/O failures → `I2CError`, `DeviceNotFoundError`
- [ ] Keep compatibility wrappers only if needed for migration, then deprecate *(not needed - clean break)*

## 3. OLED Independence Plan
- [x] Inventory required features from `yahboom_oled` (init, clear, write line, refresh)
- [x] Design your own OLED interface → `OLEDDisplay` with `begin/clear/add_text/add_line/refresh`
- [x] Choose implementation strategy → **adapter around `luma.oled` as optional dependency**
- [x] Implement text layout helpers (line wrapping, truncation, refresh strategy)
- [x] Add graceful fallback if OLED not detected → `begin()` returns `False` instead of raising

## 4. Package Architecture
- [x] Create source layout (`src/`-based package)
- [x] Suggested module structure:
  - [x] `src/raspbot/bus.py`
  - [x] `src/raspbot/robot.py`
  - [x] `src/raspbot/sensors/ultrasonic.py`
  - [x] `src/raspbot/sensors/line_tracker.py`
  - [x] `src/raspbot/sensors/ir.py`
  - [ ] `src/raspbot/inputs/button.py` *(moved to `src/raspbot/sensors/button.py` -- implemented)*
  - [x] `src/raspbot/display/oled.py`
  - [x] `src/raspbot/actuators/buzzer.py`
  - [x] `src/raspbot/actuators/led_bar.py` *(RGB light bar)*
  - [x] `src/raspbot/camera/opencv_camera.py` → `Camera` class, lazy cv2 import, context manager
  - [x] `src/raspbot/exceptions.py`
  - [x] `src/raspbot/types.py`
- [x] Keep side effects out of import time (no hardware auto-init on import)
- [x] Use typed public interfaces

## 5. Build and Metadata
- [x] Add `pyproject.toml` (PEP 517/518 build system) → hatchling
- [x] Add metadata:
  - [x] name, version, description, readme, license, classifiers
  - [x] project URLs (repo, docs, issues)
  - [x] authors/maintainers
- [x] Define runtime dependencies and optional extras (`oled`, `camera`, `dev`)
- [x] Configure wheel + sdist builds

## 6. Testing and Quality Gates
- [x] Add unit tests for pure logic (data conversion, formatting, API behavior)
- [x] Add unit tests for each peripheral API (line tracker, button, buzzer, RGB, IR, OLED)
- [x] Add hardware-in-the-loop smoke tests for real Raspberry Pi hardware *(all 18 passed on Pi)*
- [x] Add hardware smoke tests per module (file `tests/test_real_hardware.py`):
  - [x] line tracker read stability
  - [x] button read behavior → `test_button_reads_without_error`, `test_button_not_pressed_by_default`
  - [x] buzzer tone/on-off behavior
  - [x] RGB light bar color/channel mapping
  - [x] IR sensor trigger/read behavior
  - [x] OLED display init, write, refresh, context manager
  - [x] camera frame capture with OpenCV → `test_camera_*` tests in `test_real_hardware.py` (8 hardware tests added)
- [x] Add mocks/fakes for I2C bus to run CI without hardware → `tests/conftest.py` `mock_bus` fixture
- [x] Add camera test doubles to run CI when no camera device is present (mock cv2 + mock cap)
- [ ] Add linting + formatting + type checks:
  - [x] ruff (configured in `pyproject.toml`, wired into CI)
  - [x] mypy (configured in `pyproject.toml`, wired into CI)
  - [x] pytest with coverage
- [ ] Define minimum acceptable coverage for core modules

## 7. Documentation and Examples
- [x] Write README with:
  - [x] install instructions
  - [x] quickstart example
  - [x] wiring/permissions notes (I2C enabled, user groups)
  - [x] troubleshooting section
- [ ] Add API reference docs (docstrings first ✓, docs site optional)
- [ ] Provide examples equivalent to current scripts:
  - [ ] distance reading loop
  - [ ] OLED distance display
  - [ ] servo/motor basic usage
  - [ ] line tracker state display example
  - [ ] button-triggered action example *(no button hardware)*
  - [ ] buzzer alert pattern example
  - [ ] RGB light bar animation example
  - [ ] IR sensor event example
  - [ ] OpenCV camera frame capture and preview example
- [x] Add migration notes: from `Raspbot_Lib` and `yahboom_oled` to new API (in README.md)

## 8. Release Process and PyPI Publication
- [ ] Create TestPyPI and PyPI accounts
- [ ] Generate API tokens and store securely
- [ ] Build artifacts locally (`python -m build`)
- [ ] Validate distributions (`twine check dist/*`)
- [ ] Publish first to TestPyPI and verify install/import on clean venv
- [ ] Publish stable release to PyPI
- [ ] Tag release in git and write release notes/changelog

## 9. CI/CD and Maintenance
- [x] Add CI pipeline for lint, type-check, tests, and package build
- [ ] Add automated publish workflow for tagged releases (with manual approval)
- [ ] Add semantic versioning policy and changelog process
- [ ] Add issue/PR templates
- [ ] Define support matrix and deprecation policy

## 10. Immediate Next Actions (Suggested Order)
- [x] Extract current hardware operations from scripts into a draft module
- [x] Implement minimal independent class for ultrasonic sensor reads
- [x] Implement minimal independent OLED class with `init`, `clear`, `add_line`, `refresh`
- [x] Implement minimal independent classes for line tracker, buzzer, RGB light bar, and IR sensor
- [x] Implement OpenCV camera wrapper with safe open/release lifecycle → `src/raspbot/camera/opencv_camera.py`
- [ ] Replace usage in `03_test_oled.py` with your new package API
- [x] Add first tests and package metadata
- [ ] Do a TestPyPI dry run
- [ ] Push to GitHub remote *(repo created locally; push once remote is configured)*
