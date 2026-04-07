# raspbot

**Clean Python library for controlling the Yahboom Raspbot V2 robot car on Raspberry Pi.**

`raspbot` replaces two unmaintained legacy libraries (`Raspbot_Lib` and `yahboom_oled`) with a
modern, modular, fully-typed package that is installable from PyPI.

---

## Features

| Subsystem | Class | Notes |
|---|---|---|
| Motors | `Motors` | Four-wheel drive, signed or directional speed |
| Servos | `Servo`, `ServoPair` | Pan/tilt with angle clamping |
| Buzzer | `Buzzer` | Beep patterns |
| LEDs | `LedBar` | 14 WS2812 NeoPixels, indexed colour + direct RGB |
| LED effects | `LightEffects` | River, breathing, random, starlight, gradient |
| Ultrasonic | `UltrasonicSensor` | Distance in mm / cm, context manager |
| Line tracker | `LineTracker` | 4-channel IR array, frozen `LineState` dataclass |
| IR remote | `IRReceiver` | Key-code polling, context manager |
| Button | `Button` | KEY1 tactile button, polled |
| OLED display | `OLEDDisplay` | 128x32 SSD1306 via `luma.oled` (optional extra) |
| Camera | `Camera` | OpenCV VideoCapture wrapper (optional extra) |
| Cooperative tasks | `Task` | Non-blocking rate-gate, decorator factory |

---

## Quick install

```bash
pip install raspbot                        # core (I2C hardware)
pip install "raspbot[oled]"                # + OLED display
pip install "raspbot[camera]"              # + OpenCV camera
pip install "raspbot[oled,camera]"         # everything
```

---

## Quickstart

```python
import time
from raspbot import Robot

with Robot() as bot:
    bot.motors.forward(speed=150)
    time.sleep(1)
    bot.motors.stop()

    print(bot.ultrasonic.read_cm(), "cm")
```

Non-blocking loop with cooperative tasks:

```python
import time
from raspbot import Robot, Task
from raspbot.types import LedColor

with Robot() as bot:
    @Task.every(0.5)
    def blink(ct: float) -> None:
        bot.leds.set_all(LedColor.GREEN)

    @Task.every(2.0)
    def sense(ct: float) -> None:
        print(bot.ultrasonic.read_cm(), "cm")

    end = time.monotonic() + 10.0
    while time.monotonic() < end:
        ct = time.monotonic()
        blink(ct)
        sense(ct)
        time.sleep(0.001)
```

---

## Requirements

- Raspberry Pi running Raspberry Pi OS (32-bit or 64-bit)
- Python 3.10 or later
- I2C enabled (`sudo raspi-config` > Interface Options > I2C)
- User in the `i2c` group: `sudo usermod -aG i2c $USER`
- Yahboom Raspbot V2 powered on and connected via I2C bus 1

---

## Next steps

- [Getting Started](getting_started.md) -- prerequisites, wiring, first program
- [API Reference](api/robot.md) -- full class and method documentation
- [Guides](guides/cooperative_tasks.md) -- in-depth usage patterns
