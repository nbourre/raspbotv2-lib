# Buzzer

`raspbot.actuators.buzzer.Buzzer`

Controls the on-board piezo buzzer via I2C register `0x06`.

Access via `Robot.buzzer`.

The `Buzzer` is fully non-blocking.  Schedule a beep or pattern with
`beep()` / `pattern()`, then call `update(ct)` on every main-loop iteration
to advance the internal state machine.  No `time.sleep()` is ever called.

---

## Methods

### `on()`

```python
def on(self) -> None
```

Turn the buzzer on immediately (raw hardware command).

---

### `off()`

```python
def off(self) -> None
```

Turn the buzzer off immediately (raw hardware command).

---

### `beep(duration=0.2)`

```python
def beep(self, duration: float = 0.2) -> None
```

Schedule a single non-blocking beep of `duration` seconds.

The buzzer turns on immediately.  `update()` will turn it off after
`duration` seconds.  Any previously scheduled sequence is cancelled.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `duration` | `float` | `0.2` | How long to beep, in seconds |

---

### `pattern(on_time, off_time, count)`

```python
def pattern(self, on_time: float, off_time: float, count: int) -> None
```

Schedule a non-blocking repeated beep pattern.

The first beep starts immediately.  `update()` drives all subsequent
on/off transitions without blocking.

| Parameter | Type | Description |
|---|---|---|
| `on_time` | `float` | Duration of each beep (seconds) |
| `off_time` | `float` | Silence between beeps (seconds) |
| `count` | `int` | Number of beeps |

---

### `update(ct)`

```python
def update(self, ct: float) -> None
```

Advance the buzzer state machine.

Call this on **every main-loop iteration** with `ct = time.monotonic()`.
It is cheap (a float comparison) when nothing is scheduled.

| Parameter | Type | Description |
|---|---|---|
| `ct` | `float` | Current time in seconds (from `time.monotonic()`) |

---

### `is_active`

```python
@property
def is_active(self) -> bool
```

`True` while a beep or pattern is in progress.

---

## Examples

```python
import time
from raspbot import Robot

with Robot() as bot:
    # Schedule a 200 ms beep -- returns immediately
    bot.buzzer.beep(0.2)

    while True:
        ct = time.monotonic()
        bot.buzzer.update(ct)   # drives the on/off transition
        time.sleep(0.001)

    # Wait until the beep finishes before doing something else
    while bot.buzzer.is_active:
        ct = time.monotonic()
        bot.buzzer.update(ct)
        time.sleep(0.001)
```

```python
import time
from raspbot import Robot

with Robot() as bot:
    # SOS pattern -- all non-blocking
    bot.buzzer.pattern(0.1, 0.1, 3)   # ...

    while bot.buzzer.is_active:
        bot.buzzer.update(time.monotonic())
        time.sleep(0.001)

    bot.buzzer.pattern(0.3, 0.1, 3)   # ---
    # ... and so on
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
