# LED Effects

`raspbot.effects.light_effects.LightEffects`

Animated LED effect engine built on top of `LedBar`.
All effects run synchronously in the calling thread and respect a `running` flag that can be
cleared to stop the effect early.

Access via `Robot.light_effects`.

---

## Methods

### `river(duration=10.0, speed=0.05)`

```python
def river(self, duration: float = 10.0, speed: float = 0.05) -> None
```

Sequential chase-light cycling through all 7 colours.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `duration` | `float` | `10.0` | Total run time (seconds) |
| `speed` | `float` | `0.05` | Delay between each LED step (seconds) |

---

### `breathing(color=LedColor.BLUE, duration=10.0, speed=0.01)`

```python
def breathing(
    self,
    color: LedColor = LedColor.BLUE,
    duration: float = 10.0,
    speed: float = 0.01,
) -> None
```

Fade all LEDs in and out on a single colour.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `color` | `LedColor` | `BLUE` | Which colour to breathe |
| `duration` | `float` | `10.0` | Total run time (seconds) |
| `speed` | `float` | `0.01` | Delay between brightness steps (seconds) |

---

### `random_running(duration=10.0, speed=0.05)`

```python
def random_running(self, duration: float = 10.0, speed: float = 0.05) -> None
```

Randomly colour each LED every tick.

---

### `starlight(duration=10.0, speed=0.1)`

```python
def starlight(self, duration: float = 10.0, speed: float = 0.1) -> None
```

Random subset of LEDs lit, cycling through all colours.

---

### `gradient(duration=10.0, speed=0.02)`

```python
def gradient(self, duration: float = 10.0, speed: float = 0.02) -> None
```

Sequential fill with a random RGB colour, then reverse-fill (wipe in/out).

---

### `stop()`

```python
def stop(self) -> None
```

Request the currently running effect to stop after its next cycle.
Thread-safe; can be called from another thread.

---

### `off()`

```python
def off(self) -> None
```

Turn off all LEDs immediately (calls `LedBar.off_all()`).

---

## Running effects in a background thread

All effect methods are blocking.
To run an effect without stalling your main loop, run it in a `threading.Thread`:

```python
import threading
from raspbot import Robot
from raspbot.types import LedColor

with Robot() as bot:
    t = threading.Thread(
        target=bot.light_effects.breathing,
        kwargs={"color": LedColor.CYAN, "duration": 30.0},
        daemon=True,
    )
    t.start()

    # ... main loop continues here ...

    bot.light_effects.stop()  # signal the effect to stop
    t.join()
```

---

## Examples

```python
from raspbot import Robot
from raspbot.types import LedColor

with Robot() as bot:
    # River chase for 5 seconds
    bot.light_effects.river(duration=5.0)

    # Breathing blue for 8 seconds
    bot.light_effects.breathing(color=LedColor.BLUE, duration=8.0)

    # Random party mode
    bot.light_effects.random_running(duration=3.0)
```

---

## See also

- [LEDs](leds.md)
- [Robot facade](robot.md)
