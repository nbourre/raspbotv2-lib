"""
Ultrasonic distance sensor module.

Reads distance from the HC-SR04-compatible sensor wired through the Raspbot
V2 microcontroller.  The distance is returned in millimetres.

Protocol
--------
1. Enable the sensor via register 0x07.
2. Wait ≥ 60 ms for the first measurement.
3. Read high byte from register 0x1B and low byte from 0x1A.
4. Distance (mm) = (high_byte << 8) | low_byte.
5. Disable the sensor when done.
"""

from __future__ import annotations

import logging
import time

from raspbot.bus import I2CBus
from raspbot.types import Reg

logger = logging.getLogger(__name__)

_WARMUP_SECONDS = 0.06  # 60 ms warmup after enabling


class UltrasonicSensor:
    """Reads distance from the ultrasonic sensor.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self._bus = bus
        self._enabled = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def enable(self) -> None:
        """Power on the ultrasonic sensor."""
        logger.debug("Ultrasonic enable")
        self._bus.write_block_data(Reg.ULTRASONIC_SWITCH, [1])
        self._enabled = True
        time.sleep(_WARMUP_SECONDS)

    def disable(self) -> None:
        """Power off the ultrasonic sensor."""
        logger.debug("Ultrasonic disable")
        self._bus.write_block_data(Reg.ULTRASONIC_SWITCH, [0])
        self._enabled = False

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------

    def read_mm(self) -> int:
        """Return the current distance reading in millimetres.

        The sensor must be enabled before calling this method.  If the
        sensor is not enabled, it is automatically enabled and a short
        warmup delay is applied.

        Returns
        -------
        int
            Distance in millimetres.  Returns 0 if the reading is invalid.
        """
        if not self._enabled:
            self.enable()
        high = self._bus.read_block_data(Reg.ULTRASONIC_HIGH, 1)[0]
        low = self._bus.read_block_data(Reg.ULTRASONIC_LOW, 1)[0]
        distance = (high << 8) | low
        logger.debug("Ultrasonic distance=%d mm", distance)
        return distance

    def read_cm(self) -> float:
        """Return the current distance reading in centimetres."""
        return self.read_mm() / 10.0

    def __enter__(self) -> UltrasonicSensor:
        self.enable()
        return self

    def __exit__(self, *_: object) -> None:
        self.disable()
