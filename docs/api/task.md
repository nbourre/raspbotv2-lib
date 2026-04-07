# Task

`raspbot.utils.task.Task`

Non-blocking timed task utility -- the cooperative multitasking primitive used throughout the
library.

`Task` wraps a callable so that it only executes when at least `rate` seconds have elapsed since
its last execution.
Calling the task more frequently than `rate` is safe and cheap -- it simply returns without
executing.

---

## Constructor

```python
class Task:
    def __init__(
        self,
        fn: Callable[[float], Any],
        rate: float,
        run_immediately: bool = True,
    ) -> None: ...
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `fn` | `Callable[[float], Any]` | -- | Function to execute. Receives `current_time` (float) |
| `rate` | `float` | -- | Minimum interval between executions, in seconds |
| `run_immediately` | `bool` | `True` | If `True`, runs on the very first call |

---

## Calling a task

```python
task(current_time: float) -> None
```

Pass the current monotonic time. The task runs only if enough time has elapsed.

```python
import time
from raspbot.utils.task import Task

def blink(ct: float) -> None:
    print("blink at", ct)

task_blink = Task(blink, rate=0.5)

while True:
    ct = time.monotonic()
    task_blink(ct)
    time.sleep(0.001)
```

---

## Decorator factory

### `Task.every(rate, run_immediately=True)`

```python
@classmethod
def every(
    cls,
    rate: float,
    run_immediately: bool = True,
) -> Callable[[Callable[[float], Any]], Task]
```

Decorator that wraps a function as a `Task` in place.

```python
@Task.every(1.0)
def task_sensors(ct: float) -> None:
    print(bot.ultrasonic.read_cm())
```

After decoration, `task_sensors` is a `Task` instance.
Call it with `task_sensors(ct)` in the main loop.

---

## Properties and methods

### `rate`

```python
@property
def rate(self) -> float

@rate.setter
def rate(self, value: float) -> None
```

Read or update the interval between executions (seconds).

---

### `reset()`

```python
def reset(self) -> None
```

Reset the internal timer so the task fires on the very next call.

---

## `run_immediately` semantics

| `run_immediately` | First execution |
|---|---|
| `True` (default) | On the first call, regardless of elapsed time |
| `False` | After the first full `rate` period has elapsed |

---

## Examples

### Multiple tasks in a loop

```python
import time
from raspbot import Robot, Task
from raspbot.types import LedColor

with Robot() as bot:
    @Task.every(0.1)
    def read_sensor(ct: float) -> None:
        d = bot.ultrasonic.read_cm()
        if d < 15:
            bot.motors.stop()

    @Task.every(2.0)
    def blink_leds(ct: float) -> None:
        bot.leds.set_all(LedColor.GREEN)

    @Task.every(1.0)
    def print_status(ct: float) -> None:
        print("tick", ct)

    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        ct = time.monotonic()
        read_sensor(ct)
        blink_leds(ct)
        print_status(ct)
        time.sleep(0.001)
```

### Dynamically changing rate

```python
task = Task(my_fn, rate=1.0)

# Speed it up at runtime:
task.rate = 0.25
```

---

## See also

- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
- [Robot facade](robot.md)
