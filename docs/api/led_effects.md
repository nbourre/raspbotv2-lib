# LED Effects

`raspbot.effects.light_effects.LightEffects`

Animated LED effect engine built on top of `LedBar`.

Access via `Robot.light_effects`.

All effects are **non-blocking**.  Start an effect with one of the
`start_*` methods, then call `update(ct)` on every main-loop iteration to
advance the animation.  No `time.sleep()` or background threads are used.

---

## Starting effects

### `start_river(speed=0.05)`

```python
def start_river(self, speed: float = 0.05) -> None
```

Sequential chase-light cycling through all 7 colours.
A sliding 3-LED window advances one step per frame.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `speed` | `float` | `0.05` | Seconds between each LED step |

---

### `start_breathing(color=LedColor.BLUE, speed=0.01)`

```python
def start_breathing(
    self,
    color: LedColor = LedColor.BLUE,
    speed: float = 0.01,
) -> None
```

Fade all LEDs in and out on a single colour.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `color` | `LedColor` | `BLUE` | Which colour to breathe |
| `speed` | `float` | `0.01` | Seconds between brightness steps |

---

### `start_random_running(speed=0.05)`

```python
def start_random_running(self, speed: float = 0.05) -> None
```

Assign a random `LedColor` to every LED each frame.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `speed` | `float` | `0.05` | Seconds between frames |

---

### `start_starlight(speed=0.1)`

```python
def start_starlight(self, speed: float = 0.1) -> None
```

Randomly light a subset of LEDs each frame.  The active colour cycles
through all 7 colours, spending about one second on each.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `speed` | `float` | `0.1` | Seconds between frames |

---

### `start_gradient(speed=0.02)`

```python
def start_gradient(self, speed: float = 0.02) -> None
```

Fill LEDs one by one with a random saturated colour, then erase them one
by one, repeating indefinitely.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `speed` | `float` | `0.02` | Seconds between each LED step |

---

## Tick and control

### `update(ct)`

```python
def update(self, ct: float) -> None
```

Advance the current effect by one frame if enough time has elapsed.

Call this on **every main-loop iteration** with `ct = time.monotonic()`.
It is cheap (a float comparison) when gated between frames.

| Parameter | Type | Description |
|---|---|---|
| `ct` | `float` | Current time in seconds (from `time.monotonic()`) |

---

### `stop()`

```python
def stop(self) -> None
```

Cancel the current effect and turn off all LEDs immediately.

---

### `off()`

```python
def off(self) -> None
```

Alias for `stop()`.

---

### `is_active`

```python
@property
def is_active(self) -> bool
```

`True` while an effect is running.

---

## Examples

```python
import time
from raspbot import Robot
from raspbot.types import LedColor

with Robot() as bot:
    # Start breathing blue -- returns immediately
    bot.light_effects.start_breathing(LedColor.BLUE, speed=0.01)

    while True:
        ct = time.monotonic()
        bot.light_effects.update(ct)   # advances one frame when due
        time.sleep(0.001)
```

```python
import time
from raspbot import Robot

with Robot() as bot:
    # Cycle through effects
    bot.light_effects.start_river(speed=0.05)
    start = time.monotonic()

    while True:
        ct = time.monotonic()
        bot.light_effects.update(ct)

        if ct - start > 10.0:
            bot.light_effects.start_starlight(speed=0.1)
            start = ct

        time.sleep(0.001)
```

---

## See also

- [LEDs](leds.md)
- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
