# Line Tracker

`raspbot.sensors.line_tracker.LineTracker`  
`raspbot.sensors.line_tracker.LineState`

Reads the four-channel IR reflective line-tracking sensor array via I2C register `0x0A`.

Bit layout of the returned byte:

```
bit 3 : x1 (left-most sensor)
bit 2 : x2
bit 1 : x3
bit 0 : x4 (right-most sensor)
```

A bit value of `1` means the sensor detects a dark/black surface (on line).

Access via `Robot.line_tracker`.

---

## `LineState`

A frozen dataclass -- a snapshot of all four sensor channels.

```python
@dataclass(frozen=True)
class LineState:
    x1: bool   # left-most sensor
    x2: bool
    x3: bool
    x4: bool   # right-most sensor
    raw: int   # raw byte from the register
```

### Properties

#### `on_line`

```python
@property
def on_line(self) -> bool
```

`True` if any sensor detects a line.

#### `centered`

```python
@property
def centered(self) -> bool
```

`True` if both centre sensors (`x2` and `x3`) are on the line.

### `__str__()`

Returns a compact string representation, e.g. `LineState(0110)`.

---

## `LineTracker`

### Methods

#### `read()`

```python
def read(self) -> LineState
```

Read the sensor register and return a `LineState` snapshot.

---

## Examples

```python
from raspbot import Robot

with Robot() as bot:
    state = bot.line_tracker.read()
    print(state)                  # e.g. LineState(0110)
    print("On line:", state.on_line)
    print("Centered:", state.centered)

    # Individual channels
    if state.x1:
        print("Left sensor sees the line")
```

### Simple line-following loop

```python
import time
from raspbot import Robot, Task

with Robot() as bot:
    @Task.every(0.05)
    def follow(ct: float) -> None:
        s = bot.line_tracker.read()
        if not s.on_line:
            bot.motors.forward(speed=120)
        elif s.centered:
            bot.motors.forward(speed=150)
        elif s.x1 and not s.x4:
            bot.motors.turn_left(speed=100)
        elif s.x4 and not s.x1:
            bot.motors.turn_right(speed=100)

    end = time.monotonic() + 60.0
    while time.monotonic() < end:
        follow(time.monotonic())
        time.sleep(0.001)
```

---

## See also

- [Robot facade](robot.md)
- [Line Following guide](../guides/line_following.md)
