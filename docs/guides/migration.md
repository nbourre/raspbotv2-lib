# Migration Guide

This page maps the old `Raspbot_Lib` / `yahboom_oled` API to the new `raspbot` package.

---

## Overview of changes

| What changed | Old | New |
|---|---|---|
| Package name | `Raspbot_Lib` | `raspbot` |
| Install method | manual copy | `pip install raspbot` |
| I2C backend | `smbus` | `smbus2` |
| OLED driver | `Adafruit_SSD1306` | `luma.oled` (optional extra) |
| Entry point | `Raspbot()` | `Robot()` |
| Naming | `CamelCase` abbreviated | descriptive Python conventions |

---

## Motor control

| Old | New |
|---|---|
| `bot = Raspbot()` | `bot = Robot()` |
| `bot.Ctrl_Car(id, dir, speed)` | `bot.motors.set(id, dir, speed)` |
| `bot.Ctrl_Muto(id, speed)` | `bot.motors.drive(id, speed)` |
| `bot.Ctrl_Car(0, 0, 150)` (all forward) | `bot.motors.forward(150)` |
| `bot.Ctrl_Car(0, 1, 150)` (all reverse) | `bot.motors.backward(150)` |

```python
# Old
from Raspbot_Lib import Raspbot
bot = Raspbot()
bot.Ctrl_Car(0, 0, 150)

# New
from raspbot import Robot
with Robot() as bot:
    bot.motors.forward(150)
```

---

## Servo control

| Old | New |
|---|---|
| `bot.Ctrl_Servo(1, angle)` | `bot.servos.pan.set_angle(angle)` |
| `bot.Ctrl_Servo(2, angle)` | `bot.servos.tilt.set_angle(angle)` |

Note: the TILT servo is hardware-limited to 110 degrees.
The new library clamps the angle automatically.

---

## Buzzer

| Old | New |
|---|---|
| `bot.Ctrl_BEEP_Switch(1)` | `bot.buzzer.on()` |
| `bot.Ctrl_BEEP_Switch(0)` | `bot.buzzer.off()` |

---

## LEDs

| Old | New |
|---|---|
| `bot.Ctrl_WQ2812_ALL(1, color)` | `bot.leds.set_all(color)` |
| `bot.Ctrl_WQ2812_ALL(0, color)` | `bot.leds.off_all()` |
| `bot.Ctrl_WQ2812_Single(i, 1, color)` | `bot.leds.set_one(i, color)` |
| `bot.Ctrl_WQ2812_brightness_ALL(r,g,b)` | `bot.leds.set_brightness_all(r,g,b)` |
| `bot.Ctrl_WQ2812_brightness_Single(i,r,g,b)` | `bot.leds.set_brightness_one(i,r,g,b)` |

The new `LedColor` enum uses the same integer values as the old library:

```python
# Old
bot.Ctrl_WQ2812_ALL(1, 2)   # blue = 2

# New
from raspbot.types import LedColor
bot.leds.set_all(LedColor.BLUE)   # LedColor.BLUE == 2
```

---

## Ultrasonic sensor

| Old | New |
|---|---|
| `bot.Ctrl_Ulatist_Switch(1)` | `bot.ultrasonic.enable()` |
| `bot.Ctrl_Ulatist_Switch(0)` | `bot.ultrasonic.disable()` |
| `bot.read_data_array(0x1b, 1)[0]` + `bot.read_data_array(0x1a, 1)[0]` | `bot.ultrasonic.read_mm()` |

The new library reads both bytes and assembles the 16-bit value for you.

---

## Line tracker

| Old | New |
|---|---|
| `bot.Ctrl_IR_Switch(1)` (note: this was actually ultrasonic in old lib) | n/a |
| `bot.read_data_array(0x0a, 1)[0]` | `bot.line_tracker.read()` |

The new `LineTracker.read()` returns a `LineState` dataclass with named attributes (`x1`-`x4`,
`on_line`, `centered`) instead of a raw byte.

---

## IR receiver

| Old | New |
|---|---|
| `bot.Ctrl_IR_Switch(1)` | `bot.ir.enable()` |
| `bot.Ctrl_IR_Switch(0)` | `bot.ir.disable()` |
| `bot.read_data_array(0x0c, 1)[0]` | `bot.ir.read_keycode()` |

`read_keycode()` returns `None` instead of `0` when no code is available.

---

## OLED display

The new `OLEDDisplay` replaces `yahboom_oled` which used the abandoned `Adafruit_SSD1306`.

| Old | New |
|---|---|
| `from yahboom_oled import OLED` | `from raspbot.display.oled import OLEDDisplay` |
| `oled = OLED()` | `oled = OLEDDisplay()` |
| `oled.init_oled()` | `oled.begin()` |
| `oled.add_line(text, n)` | `oled.add_line(text, line=n)` |
| `oled.refresh()` | `oled.refresh()` (unchanged) |

Install the extra:

```bash
pip install "raspbot[oled]"
```

---

## Context manager (new)

The new library uses the context manager pattern to ensure clean shutdown:

```python
# Old (manual cleanup required)
bot = Raspbot()
try:
    bot.Ctrl_Car(0, 0, 150)
finally:
    bot.Ctrl_Car(0, 0, 0)

# New (automatic cleanup)
with Robot() as bot:
    bot.motors.forward(150)
# motors stopped, LEDs off, bus closed automatically
```

---

## See also

- [Getting Started](../getting_started.md)
- [Robot API reference](../api/robot.md)
- [Troubleshooting](troubleshooting.md)
