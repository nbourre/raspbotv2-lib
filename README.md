# raspbot

A clean, well-typed Python library for controlling the **Yahboom Raspbot V2** robot car on Raspberry Pi.

Replaces the original `Raspbot_Lib` and `yahboom_oled` libraries with a maintainable, dependency-minimal package that works with modern Raspberry Pi OS and Python 3.10+.

## Features

| Subsystem | Module |
|---|---|
| DC motors (4-wheel drive) | `raspbot.actuators.motors` |
| Pan/tilt servos | `raspbot.actuators.servo` |
| Piezo buzzer | `raspbot.actuators.buzzer` |
| WS2812 RGB LED bar (14 LEDs) | `raspbot.actuators.led_bar` |
| Ultrasonic distance sensor | `raspbot.sensors.ultrasonic` |
| 4-channel line tracker | `raspbot.sensors.line_tracker` |
| IR remote receiver | `raspbot.sensors.ir` |
| SSD1306 128×32 OLED display | `raspbot.display.oled` *(optional)* |
| LED animation effects | `raspbot.effects.light_effects` |

## Installation

**Core package** (motors, sensors, buzzer, LEDs — no OLED):

```bash
pip install raspbot
```

**With OLED support:**

```bash
pip install "raspbot[oled]"
```

**Development dependencies:**

```bash
pip install "raspbot[dev]"
```

## Prerequisites

### Raspberry Pi setup

1. Enable I2C: `sudo raspi-config` → Interface Options → I2C → Enable
2. Add your user to the `i2c` group: `sudo usermod -aG i2c $USER` (log out and back in)
3. Verify the device is detected: `i2cdetect -y 1` should show `2b` at address `0x2B`

### Wiring

The Raspbot V2 microcontroller communicates over I2C bus 1 at address `0x2B`.
No extra wiring is required beyond the standard Raspbot V2 assembly.

The OLED display (if present) uses I2C bus 1 at address `0x3C`.

## Quickstart

```python
import time
from raspbot import Robot

with Robot() as bot:
    # Drive forward for 1 second
    bot.motors.forward(speed=150)
    time.sleep(1)
    bot.motors.stop()

    # Read distance
    with bot.ultrasonic:
        print(bot.ultrasonic.read_cm(), "cm")

    # Beep once
    bot.buzzer.beep(0.3)

    # Light up all LEDs in blue
    from raspbot import LedColor
    bot.leds.set_all(LedColor.BLUE)
    time.sleep(1)
    bot.leds.off_all()
```

## Module examples

### Motors

```python
from raspbot import Robot, MotorId, MotorDirection

with Robot() as bot:
    bot.motors.forward(150)          # all motors forward
    bot.motors.turn_left(100)        # spin left
    bot.motors.drive(MotorId.L1, -80)  # single motor, signed speed
    bot.motors.stop()
```

### Servos

```python
with Robot() as bot:
    bot.servos.pan.set_angle(45)     # pan left
    bot.servos.tilt.set_angle(60)    # tilt up
    bot.servos.home()                # back to (90°, 25°)
```

### Ultrasonic distance

```python
with Robot() as bot:
    with bot.ultrasonic:
        while True:
            print(bot.ultrasonic.read_cm(), "cm")
            time.sleep(0.1)
```

### Line tracker

```python
with Robot() as bot:
    while True:
        state = bot.line_tracker.read()
        print(state)           # e.g. LineState(0110)
        print(state.on_line)   # True if any sensor detects line
        time.sleep(0.05)
```

### IR remote receiver

```python
with Robot() as bot:
    with bot.ir:
        while True:
            code = bot.ir.read_keycode()
            if code:
                print(f"Key: 0x{code:02X}")
            time.sleep(0.05)
```

### LED bar

```python
from raspbot import Robot, LedColor

with Robot() as bot:
    bot.leds.set_all(LedColor.RED)
    time.sleep(0.5)
    bot.leds.set_brightness_all(0, 0, 200)   # direct RGB
    time.sleep(0.5)
    bot.leds.off_all()
```

### LED effects

```python
with Robot() as bot:
    bot.light_effects.breathing(LedColor.CYAN, duration=5.0)
    bot.light_effects.river(duration=3.0, speed=0.03)
```

### OLED display

```python
from raspbot.display import OLEDDisplay

with OLEDDisplay() as oled:
    oled.clear()
    oled.add_line("Hello!", line=1)
    oled.add_line("Raspbot v2", line=2)
    oled.refresh()
```

## API reference

All public classes and methods carry docstrings.  Run `help(raspbot.Robot)` or
browse `src/raspbot/` for the full API.

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `DeviceNotFoundError: No device at I2C address 0x2B` | I2C not enabled, or wiring issue. Run `i2cdetect -y 1`. |
| `PermissionError` on `/dev/i2c-1` | User not in `i2c` group — see Prerequisites. |
| OLED import error about `luma.oled` | Install OLED extras: `pip install "raspbot[oled]"` |
| Motors don't move | Check power supply — motors need a separate 5 V supply. |

## Migration from `Raspbot_Lib` / `yahboom_oled`

| Old API | New API |
|---|---|
| `bot = Raspbot()` | `bot = Robot()` |
| `bot.Ctrl_Car(id, dir, speed)` | `bot.motors.set(id, dir, speed)` |
| `bot.Ctrl_Muto(id, speed)` | `bot.motors.drive(id, speed)` |
| `bot.Ctrl_Servo(id, angle)` | `bot.servos.pan.set_angle(angle)` / `bot.servos.tilt.set_angle(angle)` |
| `bot.Ctrl_BEEP_Switch(1)` | `bot.buzzer.on()` |
| `bot.Ctrl_WQ2812_ALL(1, color)` | `bot.leds.set_all(color)` |
| `bot.Ctrl_WQ2812_brightness_ALL(r,g,b)` | `bot.leds.set_brightness_all(r,g,b)` |
| `bot.Ctrl_Ulatist_Switch(1)` | `bot.ultrasonic.enable()` |
| `bot.read_data_array(0x1a/0x1b, 1)` | `bot.ultrasonic.read_mm()` |
| `bot.read_data_array(0x0a, 1)` | `bot.line_tracker.read()` |
| `bot.Ctrl_IR_Switch(1)` | `bot.ir.enable()` |
| `bot.read_data_array(0x0c, 1)` | `bot.ir.read_keycode()` |
| `oled.add_line(text, n)` | `oled.add_line(text, line=n)` |
| `oled.refresh()` | `oled.refresh()` *(unchanged)* |

## License

MIT
