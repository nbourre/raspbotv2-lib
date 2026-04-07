# Cooperative Tasks

This guide explains the `Task` pattern used throughout `raspbot` for non-blocking, time-driven
control loops on the Raspberry Pi.

---

## The problem with `time.sleep()`

The naive way to do "run this every 500 ms" is:

```python
while True:
    bot.leds.set_all(LedColor.GREEN)
    time.sleep(0.5)
```

This works for a single action -- but what if you need to read the ultrasonic sensor every 100 ms
*and* blink the LEDs every 500 ms *and* check the button every 50 ms -- all at the same time?

Nested `sleep()` calls quickly become a scheduling nightmare, and you cannot respond to anything
during a sleep.

---

## The rate-gate pattern

The solution is borrowed from Arduino's `millis()` pattern:

```python
ct = time.monotonic()
if ct - previous_time >= rate:
    previous_time = ct
    do_work()
```

Instead of sleeping, you check elapsed time on every iteration of a fast main loop.
The main loop sleeps for only 1 ms to yield the CPU, but checks all tasks every iteration:

```python
while True:
    ct = time.monotonic()
    if ct - t1 >= 0.1:
        t1 = ct
        read_sensor()
    if ct - t2 >= 0.5:
        t2 = ct
        blink_leds()
    time.sleep(0.001)
```

---

## `Task` encapsulates the pattern

`Task` wraps a single function with its own rate and timer:

```python
from raspbot.utils.task import Task

def blink(ct: float) -> None:
    bot.leds.set_all(LedColor.GREEN)

task_blink = Task(blink, rate=0.5)
```

Call it in the loop -- it self-throttles:

```python
while True:
    ct = time.monotonic()
    task_blink(ct)          # only actually runs every 0.5 s
    time.sleep(0.001)
```

---

## Decorator factory

`Task.every()` is a decorator that creates the `Task` in place:

```python
@Task.every(0.5)
def task_blink(ct: float) -> None:
    bot.leds.set_all(LedColor.GREEN)

@Task.every(0.1)
def task_sense(ct: float) -> None:
    global distance
    distance = bot.ultrasonic.read_cm()
```

After decoration `task_blink` and `task_sense` are `Task` instances, ready to call.

---

## Full example -- multiple concurrent tasks

```python
import time
from raspbot import Robot, Task
from raspbot.types import LedColor

with Robot() as bot:
    bot.ultrasonic.enable()
    distance = 0.0
    led_idx = 0

    @Task.every(0.1)
    def read_sensor(ct: float) -> None:
        global distance
        distance = bot.ultrasonic.read_cm()

    @Task.every(0.5)
    def cycle_leds(ct: float) -> None:
        global led_idx
        colors = list(LedColor)
        bot.leds.set_all(colors[led_idx % len(colors)])
        led_idx += 1

    @Task.every(0.2)
    def check_button(ct: float) -> None:
        if bot.button.is_pressed():
            bot.buzzer.beep(0.05)

    @Task.every(1.0)
    def print_status(ct: float) -> None:
        print(f"dist={distance:.1f}cm")

    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        ct = time.monotonic()
        read_sensor(ct)
        cycle_leds(ct)
        check_button(ct)
        print_status(ct)
        time.sleep(0.001)
```

---

## Key properties of `Task`

### `run_immediately`

By default (`run_immediately=True`) the task runs on the very first call.
Set `run_immediately=False` to wait for one full `rate` period first:

```python
task = Task(fn, rate=1.0, run_immediately=False)
```

### Dynamic rate

Change the rate at runtime:

```python
task.rate = 0.1   # speed up
task.rate = 2.0   # slow down
```

### Reset

Force the task to fire on the next call:

```python
task.reset()
```

---

## Timing accuracy

`Task` uses `time.monotonic()` which is not affected by wall-clock adjustments.
Timing accuracy is limited by:

1. The `time.sleep(0.001)` at the bottom of the loop (1 ms granularity)
2. I2C bus latency for sensor reads (~1-3 ms per transaction)
3. Python GIL contention if you use threads alongside the loop

For typical robot control rates (10-50 Hz) the accuracy is more than sufficient.

---

## See also

- [Task API reference](../api/task.md)
- [Complete robot example](../api/robot.md)
