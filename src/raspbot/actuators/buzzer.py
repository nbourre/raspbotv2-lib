"""
Buzzer control module.

Controls the piezo buzzer via I2C register 0x06.

The :class:`Buzzer` follows the cooperative tick pattern: call
:meth:`update` on every iteration of your main loop and it will switch the
buzzer on and off at the right times without ever sleeping.

Usage::

    import time
    from raspbot import RaspBot

    bot = RaspBot()

    # Schedule a single 200 ms beep
    bot.buzzer.beep(0.2)

    while True:
        ct = time.monotonic()
        bot.buzzer.update(ct)
        # ... rest of loop
"""

from __future__ import annotations

import logging
import time

from raspbot.bus import I2CBus
from raspbot.types import Reg

logger = logging.getLogger(__name__)


class Buzzer:
    """Controls the on-board piezo buzzer.

    All timed operations are non-blocking.  Schedule a beep or pattern with
    :meth:`beep` / :meth:`pattern`, then call :meth:`update` on every main-
    loop iteration to advance the internal state machine.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self._bus = bus
        # --- internal state machine ---
        # _phase_end: deadline (monotonic seconds) for the current phase,
        # or None when idle.
        self._phase_end: float | None = None
        self._on_time: float = 0.0      # on-duration for pattern beeps
        self._off_time: float = 0.0     # off-duration between pattern beeps
        self._remaining: int = 0        # beeps remaining after the current one
        self._buzzer_on: bool = False   # current hardware state
        self._pending: bool = False     # True if phase_end not yet stamped
        self._pending_duration: float = 0.0

    # ------------------------------------------------------------------
    # Immediate hardware control
    # ------------------------------------------------------------------

    def on(self) -> None:
        """Turn the buzzer on immediately."""
        logger.debug("Buzzer ON")
        self._bus.write_block_data(Reg.BEEP, [1])
        self._buzzer_on = True

    def off(self) -> None:
        """Turn the buzzer off immediately."""
        logger.debug("Buzzer OFF")
        self._bus.write_block_data(Reg.BEEP, [0])
        self._buzzer_on = False

    # ------------------------------------------------------------------
    # Schedulers (non-blocking)
    # ------------------------------------------------------------------

    def beep(self, duration: float = 0.2) -> None:
        """Schedule a single beep of *duration* seconds.

        The buzzer turns on immediately; :meth:`update` will turn it off
        after *duration* seconds.  Any previously scheduled sequence is
        cancelled.

        Parameters
        ----------
        duration:
            How long (in seconds) to keep the buzzer active.
        """
        if duration <= 0:
            return
        self._cancel()
        self._on_time = duration
        self._off_time = 0.0
        self._remaining = 0
        self._pending = True
        self._pending_duration = duration
        self.on()

    def pattern(self, on_time: float, off_time: float, count: int) -> None:
        """Schedule a repeated beep pattern.

        The first beep starts immediately; :meth:`update` drives all
        subsequent transitions.  Any previously scheduled sequence is
        cancelled.

        Parameters
        ----------
        on_time:
            Duration of each beep (seconds).
        off_time:
            Silence between beeps (seconds).
        count:
            Number of beeps.
        """
        if count <= 0 or on_time <= 0:
            return
        self._cancel()
        self._on_time = on_time
        self._off_time = off_time
        self._remaining = count - 1  # first beep starts now
        self._pending = True
        self._pending_duration = on_time
        self.on()

    # ------------------------------------------------------------------
    # Cooperative tick
    # ------------------------------------------------------------------

    def update(self, ct: float | None = None) -> None:
        """Advance the buzzer state machine.

        Call this on every main-loop iteration.  When called with no
        argument it reads the current time via :func:`time.monotonic`
        automatically, mirroring the Arduino ``millis()`` pattern.

        Parameters
        ----------
        ct:
            Current time in seconds.  Defaults to ``time.monotonic()``
            when omitted, so both calling styles are valid::

                bot.buzzer.update()       # autonomous
                bot.buzzer.update(ct)     # shared ct from the loop
        """
        if ct is None:
            ct = time.monotonic()
        # Stamp the phase deadline on the first update() after beep()/pattern()
        if self._pending:
            self._phase_end = ct + self._pending_duration
            self._pending = False
            return

        if self._phase_end is None:
            return  # idle

        if ct < self._phase_end:
            return  # phase not yet expired

        # Phase expired
        if self._buzzer_on:
            # End of an ON phase -- silence the buzzer
            self.off()
            if self._remaining > 0:
                # Start the OFF gap before the next beep
                self._phase_end = ct + self._off_time
            else:
                # Sequence finished
                self._phase_end = None
        else:
            # End of an OFF gap -- start the next ON phase
            self._remaining -= 1
            self.on()
            self._phase_end = ct + self._on_time

    # ------------------------------------------------------------------
    # State query
    # ------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """``True`` while a beep or pattern is in progress."""
        return self._phase_end is not None or self._pending

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cancel(self) -> None:
        """Cancel any in-progress sequence (does not silence hardware)."""
        self._phase_end = None
        self._pending = False
        self._remaining = 0
