# Ultrasonic Sensor

`raspbot.sensors.ultrasonic.UltrasonicSensor`

Reads distance from the HC-SR04-compatible ultrasonic sensor wired through the Raspbot V2
microcontroller.

Protocol:

1. Enable the sensor via register `0x07`
2. Wait 60 ms for the first measurement to stabilise
3. Read high byte from register `0x1B` and low byte from `0x1A`
4. Distance (mm) = `(high_byte << 8) | low_byte`
5. Disable the sensor when done

Access via `Robot.ultrasonic`.

---

## Methods

### `enable()`

```python
def enable(self) -> None
```

Power on the ultrasonic sensor and apply the 60 ms warmup delay.

---

### `disable()`

```python
def disable(self) -> None
```

Power off the ultrasonic sensor.

---

### `read_mm()`

```python
def read_mm(self) -> int
```

Return the current distance reading in millimetres.

If the sensor is not yet enabled, `enable()` is called automatically (including the warmup delay).

**Returns:** Distance in mm. Returns `0` if the reading is invalid.

---

### `read_cm()`

```python
def read_cm(self) -> float
```

Return the current distance reading in centimetres (`read_mm() / 10.0`).

---

## Context manager

`UltrasonicSensor` supports the context manager protocol.
`enable()` is called on entry and `disable()` on exit.

```python
with bot.ultrasonic:
    print(bot.ultrasonic.read_cm(), "cm")
# sensor disabled here
```

---

## Examples

```python
from raspbot import Robot

with Robot() as bot:
    # One-shot read (auto-enables)
    print(bot.ultrasonic.read_cm(), "cm")

    # Keep enabled for multiple reads
    bot.ultrasonic.enable()
    for _ in range(10):
        print(bot.ultrasonic.read_mm(), "mm")
    bot.ultrasonic.disable()

    # Context manager
    with bot.ultrasonic:
        print(bot.ultrasonic.read_cm(), "cm")
```

### Non-blocking polling with Task

```python
import time
from raspbot import Robot, Task

with Robot() as bot:
    bot.ultrasonic.enable()

    @Task.every(0.1)
    def read_distance(ct: float) -> None:
        d = bot.ultrasonic.read_cm()
        if d < 20:
            print("Obstacle at", d, "cm!")

    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        ct = time.monotonic()
        read_distance(ct)
        time.sleep(0.001)
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
