"""
KEY1 tactile button sensor.

Reads the state of the single user button on the Raspbot V2.
"""

from __future__ import annotations

import logging

from raspbot.bus import I2CBus
from raspbot.types import Reg

logger = logging.getLogger(__name__)


class Button:
    """Reader for the KEY1 tactile button on the Raspbot V2.

    The button state is polled on demand -- call :meth:`is_pressed` to get
    the current state.  No background thread or interrupt is used.

    Parameters
    ----------
    bus:
        Shared I2C bus instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self._bus = bus

    def is_pressed(self) -> bool:
        """Return ``True`` if the button is currently held down.

        Reads register ``0x0D`` from the microcontroller.  The register
        returns ``1`` when pressed and ``0`` when released.
        """
        data = self._bus.read_block_data(Reg.BUTTON, 1)
        pressed = data[0] == 1
        logger.debug("Button state: %s", "pressed" if pressed else "released")
        return pressed
