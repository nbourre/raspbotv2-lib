# Servos

`raspbot.actuators.servo.Servo`  
`raspbot.actuators.servo.ServoPair`

Controls the pan/tilt servo channels of the Raspbot V2 via I2C register `0x02`.

| Servo | Channel | Range |
|---|---|---|
| PAN (horizontal) | 1 | 0 - 180 deg |
| TILT (vertical) | 2 | 0 - 110 deg (hardware limit) |

Access via `Robot.servos` (a `ServoPair`).

---

## `Servo`

### Constructor

```python
class Servo:
    def __init__(self, bus: I2CBus, servo_id: ServoId | int) -> None: ...
```

### Properties

#### `max_angle`

```python
@property
def max_angle(self) -> int
```

Maximum allowed angle for this servo (180 for PAN, 110 for TILT).

### Methods

#### `set_angle(angle)`

```python
def set_angle(self, angle: int) -> None
```

Move the servo to `angle` degrees.
The value is clamped to `[0, max_angle]` automatically.

| Parameter | Type | Description |
|---|---|---|
| `angle` | `int` | Target angle in degrees |

#### `home()`

```python
def home(self) -> None
```

Move the servo to 90 degrees (centre position).

---

## `ServoPair`

Convenience wrapper that manages both `pan` and `tilt` servos together.
This is what `Robot.servos` exposes.

### Constructor

```python
class ServoPair:
    def __init__(self, bus: I2CBus) -> None: ...
```

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `pan` | `Servo` | PAN servo (channel 1, 0-180 deg) |
| `tilt` | `Servo` | TILT servo (channel 2, 0-110 deg) |

### Methods

#### `home()`

```python
def home(self) -> None
```

Move both servos to their default positions: pan to 90 deg, tilt to 25 deg.

---

## `ServoId`

```python
class ServoId(IntEnum):
    PAN  = 1
    TILT = 2
```

---

## Examples

```python
from raspbot import Robot

with Robot() as bot:
    # Centre both servos
    bot.servos.home()

    # Pan left / right
    bot.servos.pan.set_angle(0)    # full left
    bot.servos.pan.set_angle(180)  # full right

    # Tilt down (clamped at 110 automatically)
    bot.servos.tilt.set_angle(0)   # full down
    bot.servos.tilt.set_angle(110) # full up (hardware limit)

    # Absolute angle per channel
    bot.servos.pan.set_angle(45)
    bot.servos.tilt.set_angle(30)
```

---

## See also

- [Robot facade](robot.md)
