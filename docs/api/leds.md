# LEDs

`raspbot.actuators.led_bar.LedBar`

Controls the 14-LED WS2812 NeoPixel RGB light bar via I2C registers `0x03`, `0x04`, `0x08`,
`0x09`.

Access via `Robot.leds`.

---

## `LedColor`

Hardware-defined indexed colour codes (0-6):

```python
class LedColor(IntEnum):
    RED    = 0
    GREEN  = 1
    BLUE   = 2
    YELLOW = 3
    PURPLE = 4
    CYAN   = 5
    WHITE  = 6
```

---

## Methods

### Indexed-colour API

#### `set_all(color, *, on=True)`

```python
def set_all(self, color: LedColor | int, *, on: bool = True) -> None
```

Set all 14 LEDs to an indexed `color`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `color` | `LedColor` or `int` | -- | One of the 7 predefined colour codes |
| `on` | `bool` | `True` | `True` = light up, `False` = turn off |

---

#### `set_one(index, color, *, on=True)`

```python
def set_one(self, index: int, color: LedColor | int, *, on: bool = True) -> None
```

Set a single LED at `index` (0-13) to an indexed `color`.

---

#### `off_all()`

```python
def off_all(self) -> None
```

Turn off all 14 LEDs immediately.

---

#### `off_one(index)`

```python
def off_one(self, index: int) -> None
```

Turn off a single LED at `index`.

---

### Direct RGB brightness API

These methods bypass the indexed colour map and set raw R/G/B values (0-255 each).

#### `set_brightness_all(r, g, b)`

```python
def set_brightness_all(self, r: int, g: int, b: int) -> None
```

Set all LEDs to the given RGB brightness values simultaneously.

| Parameter | Description |
|---|---|
| `r` | Red channel 0-255 (clamped) |
| `g` | Green channel 0-255 (clamped) |
| `b` | Blue channel 0-255 (clamped) |

---

#### `set_brightness_one(index, r, g, b)`

```python
def set_brightness_one(self, index: int, r: int, g: int, b: int) -> None
```

Set a single LED at `index` to the given RGB brightness values.

---

### Properties

#### `count`

```python
@property
def count(self) -> int
```

Total number of LEDs on the bar (always `14`).

---

## Examples

```python
from raspbot import Robot
from raspbot.types import LedColor

with Robot() as bot:
    # Light all LEDs red
    bot.leds.set_all(LedColor.RED)

    # Light LED 0 green, LED 13 blue
    bot.leds.set_one(0, LedColor.GREEN)
    bot.leds.set_one(13, LedColor.BLUE)

    # Direct RGB -- orange
    bot.leds.set_brightness_all(255, 80, 0)

    # Turn off
    bot.leds.off_all()

    # Iterate all LEDs
    for i in range(bot.leds.count):
        bot.leds.set_one(i, LedColor.CYAN)
```

---

## See also

- [LED Effects](led_effects.md)
- [Robot facade](robot.md)
