# Exceptions

`raspbot.exceptions`

All exceptions raised by the `raspbot` library are subclasses of `RaspbotError`.

---

## Hierarchy

```
Exception
 └── RaspbotError
      ├── I2CError
      ├── DeviceNotFoundError
      ├── OLEDError
      └── HardwareNotReadyError
```

---

## `RaspbotError`

```python
class RaspbotError(Exception): ...
```

Base exception for all raspbot errors.
Catch this to handle any library error in one place.

```python
from raspbot.exceptions import RaspbotError

try:
    with Robot() as bot:
        ...
except RaspbotError as e:
    print("Hardware error:", e)
```

---

## `I2CError`

```python
class I2CError(RaspbotError):
    def __init__(self, operation: str, cause: BaseException | None = None) -> None: ...
    operation: str
    cause: BaseException | None
```

Raised when an I2C read or write operation fails.

| Attribute | Description |
|---|---|
| `operation` | Short description of the I2C operation that failed |
| `cause` | The underlying exception, if any |

---

## `DeviceNotFoundError`

```python
class DeviceNotFoundError(RaspbotError):
    def __init__(self, address: int, bus: int) -> None: ...
    address: int
    bus: int
```

Raised when the I2C device cannot be found on the bus (e.g. robot not powered on).

| Attribute | Description |
|---|---|
| `address` | I2C address that was not found |
| `bus` | Linux I2C bus number |

---

## `OLEDError`

```python
class OLEDError(RaspbotError): ...
```

Raised when the OLED display cannot be initialised or driven (e.g. `begin()` was not called
before `add_line()`).

---

## `HardwareNotReadyError`

```python
class HardwareNotReadyError(RaspbotError): ...
```

Raised when hardware is used before it has been initialised.

---

## Importing exceptions

```python
from raspbot.exceptions import (
    RaspbotError,
    I2CError,
    DeviceNotFoundError,
    OLEDError,
    HardwareNotReadyError,
)
```

All exceptions are also re-exported from the top-level `raspbot` package:

```python
from raspbot import RaspbotError, I2CError, DeviceNotFoundError
```

---

## See also

- [Troubleshooting guide](../guides/troubleshooting.md)
