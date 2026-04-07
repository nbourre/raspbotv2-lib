# IR Receiver

`raspbot.sensors.ir.IRReceiver`

Reads key-codes from the on-board IR remote-control receiver.

- Enable/disable via register `0x05`
- Key-code polled from register `0x0C`

Access via `Robot.ir`.

---

## Methods

### `enable()`

```python
def enable(self) -> None
```

Power on the IR receiver.

---

### `disable()`

```python
def disable(self) -> None
```

Power off the IR receiver.

---

### `read_keycode()`

```python
def read_keycode(self) -> int | None
```

Read the most recent IR key-code.

If the receiver is not yet enabled, `enable()` is called automatically.

**Returns:** Key-code byte (0-255), or `None` when no code is available (register returns 0 when
the receiver is idle).

---

## Context manager

`IRReceiver` supports the context manager protocol.
`enable()` is called on entry, `disable()` on exit.

```python
with bot.ir:
    code = bot.ir.read_keycode()
```

---

## Examples

```python
from raspbot import Robot

with Robot() as bot:
    with bot.ir:
        while True:
            code = bot.ir.read_keycode()
            if code is not None:
                print(f"Key: 0x{code:02X}")
```

### Non-blocking polling

```python
import time
from raspbot import Robot, Task

with Robot() as bot:
    bot.ir.enable()

    @Task.every(0.05)
    def check_ir(ct: float) -> None:
        code = bot.ir.read_keycode()
        if code is not None:
            print(f"IR key: 0x{code:02X}")

    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        check_ir(time.monotonic())
        time.sleep(0.001)
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
