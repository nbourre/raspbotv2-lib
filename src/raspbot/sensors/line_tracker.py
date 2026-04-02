"""
Line-tracking sensor module.

The Raspbot V2 has a 4-channel IR reflective line-tracking sensor array.
The state of all four channels is read as a single byte from register 0x0A.

Bit layout of the returned byte (bit 3 = x1, … bit 0 = x4)::

    bit 3 : sensor x1 (left-most)
    bit 2 : sensor x2
    bit 1 : sensor x3
    bit 0 : sensor x4 (right-most)

A bit value of **1** means the sensor detects a dark/black surface (on line).
A bit value of **0** means the sensor detects a light surface (off line).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from raspbot.bus import I2CBus
from raspbot.types import Reg

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LineState:
    """Snapshot of all four line-tracking sensor channels.

    Attributes
    ----------
    x1:
        Left-most sensor - ``True`` when on a dark line.
    x2:
        Second sensor from left.
    x3:
        Third sensor from left.
    x4:
        Right-most sensor - ``True`` when on a dark line.
    raw:
        Raw byte from the sensor register.
    """

    x1: bool
    x2: bool
    x3: bool
    x4: bool
    raw: int

    @property
    def on_line(self) -> bool:
        """``True`` if *any* sensor detects a line."""
        return self.x1 or self.x2 or self.x3 or self.x4

    @property
    def centered(self) -> bool:
        """``True`` if the two centre sensors (x2, x3) are on the line."""
        return self.x2 and self.x3

    def __str__(self) -> str:
        bits = "".join("1" if b else "0" for b in (self.x1, self.x2, self.x3, self.x4))
        return f"LineState({bits})"


def _parse_line_byte(raw: int) -> LineState:
    return LineState(
        x1=bool((raw >> 3) & 0x01),
        x2=bool((raw >> 2) & 0x01),
        x3=bool((raw >> 1) & 0x01),
        x4=bool(raw & 0x01),
        raw=raw,
    )


class LineTracker:
    """Reads the four-channel line-tracking sensor.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self._bus = bus

    def read(self) -> LineState:
        """Return a :class:`LineState` snapshot of all four channels."""
        raw = self._bus.read_block_data(Reg.LINE_TRACKER, 1)[0]
        state = _parse_line_byte(raw)
        logger.debug("LineTracker %s", state)
        return state
