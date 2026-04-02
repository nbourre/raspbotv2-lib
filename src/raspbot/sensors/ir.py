"""
Infrared remote-control receiver module.

The on-board IR receiver is enabled/disabled via register 0x05 and the
last received key-code is read from register 0x0C.
"""

from __future__ import annotations

import logging

from raspbot.bus import I2CBus
from raspbot.types import Reg

logger = logging.getLogger(__name__)


class IRReceiver:
    """Reads key-codes from the IR remote-control receiver.

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
        """Power on the IR receiver."""
        logger.debug("IR receiver enable")
        self._bus.write_block_data(Reg.IR_SWITCH, [1])
        self._enabled = True

    def disable(self) -> None:
        """Power off the IR receiver."""
        logger.debug("IR receiver disable")
        self._bus.write_block_data(Reg.IR_SWITCH, [0])
        self._enabled = False

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def read_keycode(self) -> int | None:
        """Read the most recent IR key-code.

        Returns
        -------
        int or None
            The key-code byte (0-255), or ``None`` if no code is available
            (register returns 0 when idle).
        """
        if not self._enabled:
            self.enable()
        data = self._bus.read_block_data(Reg.IR_KEYCODE, 1)
        code = data[0] if data else 0
        logger.debug("IR keycode=0x%02X", code)
        return code if code != 0 else None

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> IRReceiver:
        self.enable()
        return self

    def __exit__(self, *_: object) -> None:
        self.disable()
