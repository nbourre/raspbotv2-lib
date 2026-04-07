# Line Following

This guide explains how to implement a line-following robot using the `LineTracker` sensor and
the cooperative `Task` pattern.

---

## Hardware overview

The Raspbot V2 has a 4-channel IR reflective sensor array mounted at the front-bottom.

| Channel | Position |
|---|---|
| `x1` | Left-most |
| `x2` | Centre-left |
| `x3` | Centre-right |
| `x4` | Right-most |

A channel reads `True` when it detects a **dark/black surface** (the line).
A channel reads `False` when it detects a **light surface** (the floor).

The sensors produce a byte from register `0x0A`.
The `LineTracker.read()` method returns a frozen `LineState` dataclass with named attributes.

---

## Line-following logic

The classic proportional approach:

1. If both centre sensors (`x2`, `x3`) see the line: drive straight.
2. If the left sensor (`x1`) sees the line but not the right (`x4`): steer left.
3. If the right sensor (`x4`) sees the line but not the left (`x1`): steer right.
4. If no sensor sees the line: maintain last direction (or stop).

```
Sensor pattern   Action
0110             Forward (centered)
1000 / 1100      Turn left
0001 / 0011      Turn right
0000             No line -- forward slowly or stop
```

---

## Minimal line-following example

```python
import time
from raspbot import Robot, Task

with Robot() as bot:
    @Task.every(0.05)   # 20 Hz control loop
    def follow(ct: float) -> None:
        state = bot.line_tracker.read()

        if not state.on_line:
            bot.motors.forward(speed=100)   # no line -- creep forward
            return

        if state.centered:
            bot.motors.forward(speed=150)   # straight
        elif state.x1 and not state.x4:
            bot.motors.turn_left(speed=100)  # drift right, steer left
        elif state.x4 and not state.x1:
            bot.motors.turn_right(speed=100) # drift left, steer right
        else:
            bot.motors.forward(speed=120)   # ambiguous -- go straight

    end = time.monotonic() + 60.0
    while time.monotonic() < end:
        follow(time.monotonic())
        time.sleep(0.001)
```

---

## Adding obstacle avoidance

Combine line following with the ultrasonic sensor:

```python
import time
from raspbot import Robot, Task

SAFE_MM = 200   # stop if obstacle is closer than 20 cm

with Robot() as bot:
    bot.ultrasonic.enable()
    distance_mm = 9999

    @Task.every(0.1)
    def read_distance(ct: float) -> None:
        global distance_mm
        distance_mm = bot.ultrasonic.read_mm()

    @Task.every(0.05)
    def follow(ct: float) -> None:
        if distance_mm < SAFE_MM:
            bot.motors.stop()
            return

        state = bot.line_tracker.read()
        if not state.on_line:
            bot.motors.forward(speed=100)
        elif state.centered:
            bot.motors.forward(speed=150)
        elif state.x1 and not state.x4:
            bot.motors.turn_left(speed=100)
        elif state.x4 and not state.x1:
            bot.motors.turn_right(speed=100)
        else:
            bot.motors.forward(speed=120)

    end = time.monotonic() + 120.0
    while time.monotonic() < end:
        ct = time.monotonic()
        read_distance(ct)
        follow(ct)
        time.sleep(0.001)

    bot.motors.stop()
```

---

## Tuning tips

- **Speed:** Reduce speed if the robot overshoots turns.
  A good starting point is 100-150 for forward and 80-120 for turns.
- **Control rate:** 20-50 Hz (`rate=0.02` to `rate=0.05`) works well.
  Faster is better for tight curves.
- **Track width:** The Raspbot V2 sensor spacing works best with a track line approximately
  20-25 mm wide (standard black electrical tape).
- **`x1` / `x4` weight:** If the robot oscillates, reduce turn speed or add a hysteresis
  condition (only turn if the outer sensor has been active for 2+ consecutive reads).

---

## Reading raw sensor data

For debugging, print the `LineState` string directly:

```python
while True:
    print(bot.line_tracker.read())   # e.g. LineState(0110)
    time.sleep(0.05)
```

The four binary digits correspond to `x1 x2 x3 x4` from left to right.

---

## See also

- [LineTracker API reference](../api/line_tracker.md)
- [Cooperative Tasks guide](cooperative_tasks.md)
- [Ultrasonic Sensor API reference](../api/ultrasonic.md)
