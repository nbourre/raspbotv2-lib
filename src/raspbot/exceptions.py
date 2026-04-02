"""
Exceptions raised by the raspbot library.
"""

from __future__ import annotations


class RaspbotError(Exception):
    """Base exception for all raspbot errors."""


class I2CError(RaspbotError):
    """Raised when an I2C read or write operation fails."""

    def __init__(self, operation: str, cause: BaseException | None = None) -> None:
        msg = f"I2C error during {operation}"
        if cause is not None:
            msg = f"{msg}: {cause}"
        super().__init__(msg)
        self.operation = operation
        self.cause = cause


class DeviceNotFoundError(RaspbotError):
    """Raised when the I2C device cannot be found on the bus."""

    def __init__(self, address: int, bus: int) -> None:
        super().__init__(
            f"No device at I2C address 0x{address:02X} on bus {bus}"
        )
        self.address = address
        self.bus = bus


class OLEDError(RaspbotError):
    """Raised when the OLED display cannot be initialised or driven."""


class HardwareNotReadyError(RaspbotError):
    """Raised when hardware is used before it has been initialised."""
