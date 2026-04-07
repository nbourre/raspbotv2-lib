# Motors

`raspbot.actuators.motors.Motors`

Controls the four DC drive motors of the Raspbot V2 via I2C register `0x01`.

Motor layout (viewed from above):

```
L1 (front-left)   R1 (front-right)
L2 (rear-left)    R2 (rear-right)
```

Access via `Robot.motors`.

---

## Enumerations

### `MotorId`

```python
class MotorId(IntEnum):
    L1 = 0  # Left front
    L2 = 1  # Left rear
    R1 = 2  # Right front
    R2 = 3  # Right rear
```

### `MotorDirection`

```python
class MotorDirection(IntEnum):
    FORWARD = 0
    REVERSE = 1
```

---

## Methods

### `forward(speed=150)`

```python
def forward(self, speed: int = 150) -> None
```

Drive all four motors forward at `speed`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `speed` | `int` | `150` | PWM duty-cycle 0-255 |

---

### `backward(speed=150)`

```python
def backward(self, speed: int = 150) -> None
```

Drive all four motors backward at `speed`.

---

### `turn_left(speed=150)`

```python
def turn_left(self, speed: int = 150) -> None
```

Spin left in place: right motors forward, left motors reverse.

---

### `turn_right(speed=150)`

```python
def turn_right(self, speed: int = 150) -> None
```

Spin right in place: left motors forward, right motors reverse.

---

### `stop()`

```python
def stop(self) -> None
```

Stop all motors immediately (speed = 0).

---

### `set(motor_id, direction, speed)`

```python
def set(
    self,
    motor_id: MotorId | int,
    direction: MotorDirection | int,
    speed: int,
) -> None
```

Set direction and speed for a single motor.

| Parameter | Type | Description |
|---|---|---|
| `motor_id` | `MotorId` or `int` | Which motor (0-3) |
| `direction` | `MotorDirection` or `int` | `0` = forward, `1` = reverse |
| `speed` | `int` | 0-255 (clamped automatically) |

---

### `drive(motor_id, speed)`

```python
def drive(self, motor_id: MotorId | int, speed: int) -> None
```

Drive a single motor with a signed speed value.
Negative speed drives in reverse.

| Parameter | Type | Description |
|---|---|---|
| `motor_id` | `MotorId` or `int` | Which motor |
| `speed` | `int` | -255 to +255 |

---

## Examples

```python
from raspbot import Robot
from raspbot.types import MotorId, MotorDirection

with Robot() as bot:
    # High-level helpers
    bot.motors.forward(speed=200)
    bot.motors.stop()

    # Single motor control
    bot.motors.set(MotorId.L1, MotorDirection.FORWARD, 180)

    # Signed speed
    bot.motors.drive(MotorId.R1, -150)   # reverse at speed 150
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
