# Button

`raspbot.sensors.button.Button`

Reader for the KEY1 tactile button on the Raspbot V2.

The button state is polled on demand -- no background thread or interrupt is used.
Register `0x0D` returns `1` when pressed, `0` when released.

Access via `Robot.button`.

---

## Methods

### `is_pressed()`

```python
def is_pressed(self) -> bool
```

Return `True` if the button is currently held down.

---

## Examples

```python
from raspbot import Robot

with Robot() as bot:
    if bot.button.is_pressed():
        print("Button is held down")
```

### Wait for a button press

```python
import time
from raspbot import Robot

with Robot() as bot:
    print("Press the button...")
    while not bot.button.is_pressed():
        time.sleep(0.02)
    print("Button pressed!")
```

### Non-blocking polling

```python
import time
from raspbot import Robot, Task

with Robot() as bot:
    @Task.every(0.1)
    def check_button(ct: float) -> None:
        if bot.button.is_pressed():
            bot.buzzer.beep(0.05)

    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        check_button(time.monotonic())
        time.sleep(0.001)
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
