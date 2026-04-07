# Mecanum Wheels

The Yahboom Raspbot V2 uses **mecanum wheels** -- wheels with small rollers mounted at 45 degrees
around the rim.
By controlling the direction of each wheel independently, the robot can move sideways, diagonally,
and rotate in place without changing its heading.

All mecanum methods are part of the `Motors` class and are accessed via `Robot.motors`.

---

## Roller orientation

The Raspbot V2 uses the standard **X-pattern**:

```
Front-left  (/): rollers at +45 deg
Front-right (\): rollers at -45 deg
Rear-left   (\): rollers at -45 deg
Rear-right  (/): rollers at +45 deg
```

Viewed from above with the front of the robot at the top:

```
  FL (/)   FR (\)
  RL (\)   RR (/)
```

---

## Movement table

`F` = forward, `R` = reverse, `0` = stopped.

| Method | FL (L1) | RL (L2) | FR (R1) | RR (R2) | Result |
|---|---|---|---|---|---|
| `forward()` | F | F | F | F | Straight ahead |
| `backward()` | R | R | R | R | Straight back |
| `turn_left()` | R | R | F | F | Rotate left in place |
| `turn_right()` | F | F | R | R | Rotate right in place |
| `strafe_right()` | F | R | R | F | Slide right |
| `strafe_left()` | R | F | F | R | Slide left |
| `diagonal_forward_right()` | F | 0 | 0 | F | 45 deg fwd-right |
| `diagonal_forward_left()` | 0 | F | F | 0 | 45 deg fwd-left |
| `diagonal_backward_right()` | R | 0 | 0 | R | 45 deg bwd-right |
| `diagonal_backward_left()` | 0 | R | R | 0 | 45 deg bwd-left |

---

## Methods

### `strafe_right(speed=150)`

```python
def strafe_right(self, speed: int = 150) -> None
```

Slide directly right without rotating.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `speed` | `int` | `150` | PWM duty-cycle 0-255 |

---

### `strafe_left(speed=150)`

```python
def strafe_left(self, speed: int = 150) -> None
```

Slide directly left without rotating.

---

### `diagonal_forward_right(speed=150)`

```python
def diagonal_forward_right(self, speed: int = 150) -> None
```

Drive diagonally forward-right at 45 degrees.
Only the front-left (L1) and rear-right (R2) motors are driven; the other two are stopped.

!!! note
    Diagonal moves use only two motors so the effective thrust is lower than forward/strafe at
    the same speed. Increase speed by about 40 % to compensate if needed.

---

### `diagonal_forward_left(speed=150)`

```python
def diagonal_forward_left(self, speed: int = 150) -> None
```

Drive diagonally forward-left at 45 degrees.
Rear-left (L2) and front-right (R1) are driven.

---

### `diagonal_backward_right(speed=150)`

```python
def diagonal_backward_right(self, speed: int = 150) -> None
```

Drive diagonally backward-right at 45 degrees.
Front-left (L1) and rear-right (R2) are driven in reverse.

---

### `diagonal_backward_left(speed=150)`

```python
def diagonal_backward_left(self, speed: int = 150) -> None
```

Drive diagonally backward-left at 45 degrees.
Rear-left (L2) and front-right (R1) are driven in reverse.

---

## Complete example

```python
import time
from raspbot import Robot

SPEED = 150
DURATION = 1.0

moves = [
    ("Forward",            lambda bot: bot.motors.forward(SPEED)),
    ("Backward",           lambda bot: bot.motors.backward(SPEED)),
    ("Rotate left",        lambda bot: bot.motors.turn_left(SPEED)),
    ("Rotate right",       lambda bot: bot.motors.turn_right(SPEED)),
    ("Strafe right",       lambda bot: bot.motors.strafe_right(SPEED)),
    ("Strafe left",        lambda bot: bot.motors.strafe_left(SPEED)),
    ("Diagonal fwd-right", lambda bot: bot.motors.diagonal_forward_right(SPEED)),
    ("Diagonal fwd-left",  lambda bot: bot.motors.diagonal_forward_left(SPEED)),
    ("Diagonal bwd-right", lambda bot: bot.motors.diagonal_backward_right(SPEED)),
    ("Diagonal bwd-left",  lambda bot: bot.motors.diagonal_backward_left(SPEED)),
]

with Robot() as bot:
    for name, move_fn in moves:
        print(name)
        move_fn(bot)
        time.sleep(DURATION)
        bot.motors.stop()
        time.sleep(0.3)
```

---

## Troubleshooting

### Strafe direction is reversed

The roller orientation of your wheels may be mirrored relative to the X-pattern.
Swap `strafe_right` and `strafe_left` calls, or physically swap the front-left and front-right
wheels.

### Diagonal moves drift sideways

This is normal -- without encoders, wheel speed differences accumulate over time.
Diagonal moves are best used for short bursts, not sustained navigation.

### Robot rotates instead of strafing

The wheels are not in the X-pattern. Check that the roller axis on each wheel forms an X when
viewed from above:

```
  /  \
  \  /
```

If it forms an O (all rollers parallel), swap the left-side wheels front-to-rear.

---

## See also

- [Motors API reference](motors.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
- [examples/14_mecanum.py](https://github.com/your-org/raspbot/blob/main/examples/14_mecanum.py)
