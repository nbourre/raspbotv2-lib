"""
Non-blocking timed task utility.

Provides :class:`Task`, a lightweight cooperative multitasking primitive
that mirrors the rate-gate pattern taught in Arduino courses::

    ct = millis();
    if (ct - previousTime < rate) return;
    previousTime = ct;

Usage::

    import time
    from raspbot.utils.task import Task

    def blink(ct: float) -> None:
        ...  # runs every 500 ms

    task_blink = Task(blink, rate=0.5)

    while True:
        ct = time.monotonic()
        task_blink(ct)
        time.sleep(0.001)

Tasks can also be used as decorators::

    @Task.every(1.0)
    def task_read(ct: float) -> None:
        print("tick")

    while True:
        ct = time.monotonic()
        task_read(ct)
        time.sleep(0.001)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Task:
    """Non-blocking timed task.

    Wraps a callable so that it only executes when at least *rate* seconds
    have elapsed since its last execution.  Calling the task more frequently
    than *rate* is safe and cheap -- it simply returns without executing.

    Parameters
    ----------
    fn:
        The function to execute.  It receives the current time (as returned
        by :func:`time.monotonic`) as its only positional argument.
    rate:
        Minimum interval between executions, in seconds.
    run_immediately:
        If ``True`` (default), the task runs on the very first call
        regardless of elapsed time.  If ``False``, it waits for one full
        *rate* period before the first execution.

    Examples
    --------
    Basic usage::

        def beep(ct: float) -> None:
            bot.buzzer.beep(0.05)

        task_beep = Task(beep, rate=2.0)

        while True:
            ct = time.monotonic()
            task_beep(ct)
            time.sleep(0.001)

    Decorator usage::

        @Task.every(0.5)
        def task_blink(ct: float) -> None:
            bot.leds.set_all(LedColor.GREEN)
    """

    def __init__(
        self,
        fn: Callable[[float], Any],
        rate: float,
        run_immediately: bool = True,
    ) -> None:
        self._fn = fn
        self._rate = rate
        # When run_immediately=True: set previous_time to -rate so elapsed
        # time on the first call is at least rate regardless of ct value.
        # When run_immediately=False: set previous_time to 0.0 so the task
        # waits for one full rate period from the first call at ct >= rate.
        self._previous_time: float = -rate if run_immediately else 0.0

    # ------------------------------------------------------------------
    # Callable interface
    # ------------------------------------------------------------------

    def __call__(self, current_time: float) -> None:
        """Execute the task if enough time has elapsed.

        Parameters
        ----------
        current_time:
            The current time in seconds, typically from :func:`time.monotonic`.
        """
        if current_time - self._previous_time < self._rate:
            return
        self._previous_time = current_time
        self._fn(current_time)

    # ------------------------------------------------------------------
    # Decorator factory
    # ------------------------------------------------------------------

    @classmethod
    def every(
        cls,
        rate: float,
        run_immediately: bool = True,
    ) -> Callable[[Callable[[float], Any]], Task]:
        """Decorator that wraps a function as a :class:`Task`.

        Parameters
        ----------
        rate:
            Interval between executions in seconds.
        run_immediately:
            Whether to run on the very first call.

        Example
        -------
        ::

            @Task.every(1.0)
            def task_sensors(ct: float) -> None:
                print(bot.ultrasonic.read_cm())
        """

        def decorator(fn: Callable[[float], Any]) -> Task:
            return cls(fn, rate=rate, run_immediately=run_immediately)

        return decorator

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def rate(self) -> float:
        """Interval between executions in seconds."""
        return self._rate

    @rate.setter
    def rate(self, value: float) -> None:
        self._rate = value

    def reset(self) -> None:
        """Reset the timer so the task fires on the next call."""
        self._previous_time = -self._rate

    def __repr__(self) -> str:
        return f"Task(fn={self._fn.__name__!r}, rate={self._rate}s)"
