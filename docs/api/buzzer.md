# Buzzer

`raspbot.actuators.buzzer.Buzzer`

Controls the on-board piezo buzzer via I2C register `0x06`.

Access via `Robot.buzzer`.

---

## Methods

### `on()`

```python
def on(self) -> None
```

Turn the buzzer on continuously.

---

### `off()`

```python
def off(self) -> None
```

Turn the buzzer off.

---

### `beep(duration=0.2)`

```python
def beep(self, duration: float = 0.2) -> None
```

Sound the buzzer for `duration` seconds, then silence it.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `duration` | `float` | `0.2` | How long to beep, in seconds |

!!! note
    `beep()` uses `time.sleep()` internally, so it blocks the calling thread.
    For non-blocking beep patterns in a cooperative loop, call `buzzer.on()` / `buzzer.off()`
    from separate `Task` callbacks.

---

### `pattern(on_time, off_time, count)`

```python
def pattern(self, on_time: float, off_time: float, count: int) -> None
```

Produce a repeated beep pattern.

| Parameter | Type | Description |
|---|---|---|
| `on_time` | `float` | Duration of each beep (seconds) |
| `off_time` | `float` | Silence between beeps (seconds) |
| `count` | `int` | Number of beeps |

---

## Examples

```python
from raspbot import Robot

with Robot() as bot:
    # Single short beep
    bot.buzzer.beep(0.1)

    # SOS pattern (simplified)
    bot.buzzer.pattern(on_time=0.1, off_time=0.1, count=3)   # ...
    bot.buzzer.pattern(on_time=0.3, off_time=0.1, count=3)   # ---
    bot.buzzer.pattern(on_time=0.1, off_time=0.1, count=3)   # ...

    # Manual on/off
    bot.buzzer.on()
    # (do something)
    bot.buzzer.off()
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
