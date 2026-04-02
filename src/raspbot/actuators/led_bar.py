"""
WS2812 RGB LED bar control module.

The Raspbot V2 carries 14 WS2812 NeoPixel LEDs controlled via I2C registers
0x03 (all LEDs), 0x04 (single LED), 0x08 (brightness all), 0x09 (brightness
single).

Colour *codes* (0-6) are hardware-defined indexed colours.  For direct RGB
brightness control use the ``set_brightness`` / ``set_brightness_all`` methods.
"""

from __future__ import annotations

import logging

from raspbot.bus import I2CBus
from raspbot.types import NUM_LEDS, LedColor, Reg

logger = logging.getLogger(__name__)

_COLOR_OFF = LedColor.RED  # colour argument is ignored when state=0


def _clamp_u8(v: int) -> int:
    return max(0, min(255, v))


class LedBar:
    """Controls the 14-LED WS2812 RGB light bar.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self._bus = bus

    # ------------------------------------------------------------------
    # Indexed-colour API (0-6)
    # ------------------------------------------------------------------

    def set_all(self, color: LedColor | int, *, on: bool = True) -> None:
        """Set all LEDs to an indexed *color*.

        Parameters
        ----------
        color:
            One of the 7 predefined :class:`~raspbot.types.LedColor` codes.
        on:
            ``True`` to light up, ``False`` to turn off.
        """
        state = 1 if on else 0
        logger.debug("LED all state=%d color=%d", state, int(color))
        self._bus.write_block_data(Reg.LED_ALL, [state, int(color)])

    def set_one(self, index: int, color: LedColor | int, *, on: bool = True) -> None:
        """Set a single LED by *index* (0-based) to an indexed *color*.

        Parameters
        ----------
        index:
            LED index 0-13.
        color:
            One of the 7 predefined :class:`~raspbot.types.LedColor` codes.
        on:
            ``True`` to light up, ``False`` to turn off.
        """
        state = 1 if on else 0
        logger.debug("LED %d state=%d color=%d", index, state, int(color))
        self._bus.write_block_data(Reg.LED_SINGLE, [index, state, int(color)])

    def off_all(self) -> None:
        """Turn off all LEDs immediately."""
        self.set_all(LedColor.RED, on=False)

    def off_one(self, index: int) -> None:
        """Turn off a single LED at *index*."""
        self.set_one(index, LedColor.RED, on=False)

    # ------------------------------------------------------------------
    # Direct RGB brightness API
    # ------------------------------------------------------------------

    def set_brightness_all(self, r: int, g: int, b: int) -> None:
        """Set the RGB brightness of **all** LEDs simultaneously.

        Parameters
        ----------
        r, g, b:
            Red, green, blue channel brightness 0-255.
        """
        r, g, b = _clamp_u8(r), _clamp_u8(g), _clamp_u8(b)
        logger.debug("LED brightness all R=%d G=%d B=%d", r, g, b)
        self._bus.write_block_data(Reg.LED_BRIGHTNESS_ALL, [r, g, b])

    def set_brightness_one(self, index: int, r: int, g: int, b: int) -> None:
        """Set the RGB brightness of a single LED at *index*.

        Parameters
        ----------
        index:
            LED index 0-13.
        r, g, b:
            Red, green, blue channel brightness 0-255.
        """
        r, g, b = _clamp_u8(r), _clamp_u8(g), _clamp_u8(b)
        logger.debug("LED brightness %d R=%d G=%d B=%d", index, r, g, b)
        self._bus.write_block_data(Reg.LED_BRIGHTNESS_SINGLE, [index, r, g, b])

    @property
    def count(self) -> int:
        """Total number of LEDs on the bar."""
        return NUM_LEDS
