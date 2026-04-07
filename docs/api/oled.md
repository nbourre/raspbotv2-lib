# OLED Display

`raspbot.display.oled.OLEDDisplay`

128x32 SSD1306 OLED display controller using `luma.oled` as the hardware driver and Pillow for
framebuffer rendering.

!!! warning "Optional extra"
    This module requires the `oled` extras group:

    ```bash
    pip install "raspbot[oled]"
    ```

    Importing without `luma.oled` and `Pillow` raises `ImportError` with a helpful message.

---

## Constructor

```python
class OLEDDisplay:
    def __init__(
        self,
        i2c_port: int = 1,
        i2c_address: int = 0x3C,
    ) -> None: ...
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `i2c_port` | `int` | `1` | Linux I2C bus number |
| `i2c_address` | `int` | `0x3C` | I2C address of the SSD1306 |

The display is **not** initialised until `begin()` is called, keeping import-time side-effect free.

---

## Methods

### `begin()`

```python
def begin(self) -> bool
```

Initialise the OLED hardware.

**Returns:** `True` on success, `False` if the display cannot be found (e.g. not connected).

---

### `clear(refresh=False)`

```python
def clear(self, refresh: bool = False) -> None
```

Blank the framebuffer.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `refresh` | `bool` | `False` | Push blank frame to display immediately |

---

### `add_text(x, y, text, refresh=False)`

```python
def add_text(self, x: int, y: int, text: str, refresh: bool = False) -> None
```

Draw `text` at pixel coordinates `(x, y)`.
The origin is the top-left corner.
Coordinates outside the 128x32 panel are silently ignored.

---

### `add_line(text, line=1, refresh=False)`

```python
def add_line(self, text: str, line: int = 1, refresh: bool = False) -> None
```

Write `text` to one of the four logical display lines (1-4, top to bottom).
Each line is 8 pixels tall.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `text` | `str` | -- | String to render |
| `line` | `int` | `1` | Line number 1-4 |
| `refresh` | `bool` | `False` | Push to display immediately |

---

### `refresh()`

```python
def refresh(self) -> None
```

Push the current framebuffer to the physical OLED display.

---

## Context manager

`OLEDDisplay` supports the context manager protocol.
`begin()` is called on entry; the display is cleared on exit.

```python
with OLEDDisplay() as oled:
    oled.add_line("Hello!", line=1)
    oled.refresh()
```

---

## Constants

| Constant | Value | Description |
|---|---|---|
| `OLED_WIDTH` | `128` | Panel width in pixels |
| `OLED_HEIGHT` | `32` | Panel height in pixels |

---

## Examples

```python
from raspbot.display.oled import OLEDDisplay

oled = OLEDDisplay()
if oled.begin():
    oled.clear()
    oled.add_line("raspbot v2", line=1)
    oled.add_line("Running...", line=2)
    oled.refresh()
```

### Live sensor display

```python
import time
from raspbot import Robot, Task
from raspbot.display.oled import OLEDDisplay

with Robot() as bot:
    oled = OLEDDisplay()
    oled.begin()
    bot.ultrasonic.enable()

    @Task.every(0.2)
    def update_display(ct: float) -> None:
        d = bot.ultrasonic.read_cm()
        oled.clear()
        oled.add_line(f"Dist: {d:.1f} cm", line=1)
        oled.refresh()

    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        update_display(time.monotonic())
        time.sleep(0.001)
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
