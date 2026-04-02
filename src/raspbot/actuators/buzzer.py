"""
Buzzer control module.

Controls the piezo buzzer via I2C register 0x06.
"""

from __future__ import annotations

import logging
import time

from raspbot.bus import I2CBus
from raspbot.types import Reg

logger = logging.getLogger(__name__)


class Buzzer:
    """Controls the on-board piezo buzzer.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self._bus = bus

    def on(self) -> None:
        """Turn the buzzer on."""
        logger.debug("Buzzer ON")
        self._bus.write_block_data(Reg.BEEP, [1])

    def off(self) -> None:
        """Turn the buzzer off."""
        logger.debug("Buzzer OFF")
        self._bus.write_block_data(Reg.BEEP, [0])

    def beep(self, duration: float = 0.2) -> None:
        """Sound the buzzer for *duration* seconds, then silence it.

        Parameters
        ----------
        duration:
            How long (in seconds) to keep the buzzer active.
        """
        self.on()
        time.sleep(duration)
        self.off()

    def pattern(self, on_time: float, off_time: float, count: int) -> None:
        """Produce a repeated beep pattern.

        Parameters
        ----------
        on_time:
            Duration of each beep (seconds).
        off_time:
            Silence between beeps (seconds).
        count:
            Number of beeps.
        """
        for _ in range(count):
            self.beep(on_time)
            time.sleep(off_time)
