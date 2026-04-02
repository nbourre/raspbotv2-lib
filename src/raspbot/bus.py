"""
Low-level I2C bus helper.

Wraps ``smbus2`` and converts OS/hardware errors into raspbot exceptions so
callers never need to import smbus2 directly.
"""

from __future__ import annotations

import logging
import sys
from typing import Sequence

# smbus2 is a Linux-only package that depends on fcntl.  Guard the import so
# that the module can be loaded on non-Linux systems (e.g. for unit testing).
if sys.platform != "win32":
    import smbus2
else:  # pragma: no cover
    smbus2 = None  # type: ignore[assignment]

from raspbot.exceptions import DeviceNotFoundError, I2CError
from raspbot.types import RASPBOT_I2C_ADDRESS, RASPBOT_I2C_BUS

logger = logging.getLogger(__name__)


class I2CBus:
    """Thread-unsafe single-device I2C bus wrapper.

    Parameters
    ----------
    address:
        7-bit I2C address of the target device.
    bus:
        Linux I2C bus number (``/dev/i2c-<bus>``).
    """

    def __init__(
        self,
        address: int = RASPBOT_I2C_ADDRESS,
        bus: int = RASPBOT_I2C_BUS,
    ) -> None:
        self._address = address
        self._bus_num = bus
        try:
            self._bus = smbus2.SMBus(bus)
        except OSError as exc:
            raise DeviceNotFoundError(address, bus) from exc

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def write_byte_data(self, reg: int, value: int) -> None:
        """Write a single byte *value* to *reg*."""
        try:
            self._bus.write_byte_data(self._address, reg, value)
        except OSError as exc:
            raise I2CError(f"write_byte_data(reg=0x{reg:02X})", exc) from exc

    def write_block_data(self, reg: int, data: Sequence[int]) -> None:
        """Write a block of bytes starting at *reg*."""
        try:
            self._bus.write_i2c_block_data(self._address, reg, list(data))
        except OSError as exc:
            raise I2CError(f"write_block_data(reg=0x{reg:02X})", exc) from exc

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def read_block_data(self, reg: int, length: int) -> list[int]:
        """Read *length* bytes starting at *reg* and return them as a list."""
        try:
            return self._bus.read_i2c_block_data(self._address, reg, length)
        except OSError as exc:
            raise I2CError(f"read_block_data(reg=0x{reg:02X}, len={length})", exc) from exc

    def read_byte_data(self, reg: int) -> int:
        """Read a single byte from *reg*."""
        try:
            return self._bus.read_byte_data(self._address, reg)
        except OSError as exc:
            raise I2CError(f"read_byte_data(reg=0x{reg:02X})", exc) from exc

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Release the underlying bus file descriptor."""
        try:
            self._bus.close()
        except OSError:
            pass

    def __enter__(self) -> "I2CBus":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
