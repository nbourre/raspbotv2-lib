# Robot

`raspbot.robot.Robot`

The `Robot` class is the single entry-point for the entire library.
It owns a shared `I2CBus` instance and wires all hardware subsystems together so you never have to
manage bus references manually.

---

## Class signature

```python
class Robot:
    def __init__(
        self,
        i2c_address: int = 0x2B,
        i2c_bus: int = 1,
        camera_device: int | str = 0,
    ) -> None: ...
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `i2c_address` | `int` | `0x2B` | I2C address of the Raspbot V2 microcontroller |
| `i2c_bus` | `int` | `1` | Linux I2C bus number |
| `camera_device` | `int` or `str` | `0` | Camera device index or path (e.g. `"/dev/video0"`) |

---

## Attributes

All subsystems are created during `__init__` but hardware is only touched when you call a method
on them.

| Attribute | Type | Description |
|---|---|---|
| `motors` | `Motors` | Four-wheel drive motor controller |
| `servos` | `ServoPair` | Pan/tilt servo pair |
| `button` | `Button` | KEY1 tactile user button |
| `buzzer` | `Buzzer` | Piezo buzzer |
| `leds` | `LedBar` | 14-LED WS2812 RGB light bar |
| `ultrasonic` | `UltrasonicSensor` | HC-SR04 distance sensor |
| `line_tracker` | `LineTracker` | 4-channel IR line-tracking array |
| `ir` | `IRReceiver` | IR remote-control receiver |
| `light_effects` | `LightEffects` | Animated LED effect engine |
| `camera` | `Camera` | OpenCV VideoCapture wrapper |

---

## Methods

### `close()`

```python
def close(self) -> None
```

Safely stops all actuators and releases the I2C bus.

- Calls `motors.stop()`
- Calls `leds.off_all()`
- Calls `buzzer.off()`
- Calls `camera.close()`
- Closes the I2C bus

Each step is wrapped in `contextlib.suppress(Exception)` so a single failing subsystem does not
prevent the others from shutting down cleanly.

---

## Context manager

`Robot` implements the context manager protocol.
Using `with Robot() as bot:` is the recommended pattern -- it guarantees `close()` is called even
if an exception is raised.

```python
from raspbot import Robot

with Robot() as bot:
    bot.motors.forward(speed=150)
    # ... do work ...
# close() called automatically here
```

---

## Examples

### Basic usage

```python
import time
from raspbot import Robot

with Robot() as bot:
    bot.motors.forward(speed=150)
    time.sleep(1)
    bot.motors.stop()
    print(bot.ultrasonic.read_cm(), "cm")
```

### Custom I2C address

```python
# If your board is at a non-default address:
with Robot(i2c_address=0x2C) as bot:
    ...
```

### With camera

```python
from raspbot import Robot

with Robot(camera_device=0) as bot:
    if bot.camera.open():
        frame = bot.camera.read_frame()
        print("Frame shape:", frame.shape if frame is not None else "none")
```

---

## See also

- [Motors](motors.md)
- [Servos](servos.md)
- [Buzzer](buzzer.md)
- [LEDs](leds.md)
- [Ultrasonic Sensor](ultrasonic.md)
- [Line Tracker](line_tracker.md)
- [IR Receiver](ir_receiver.md)
- [Button](button.md)
- [Camera](camera.md)
- [LED Effects](led_effects.md)
- [Task](task.md)
