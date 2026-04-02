"""
LED light animation effects engine.

Provides the same visual effects as the original ``LightShow`` class but
built on top of the new :class:`~raspbot.actuators.led_bar.LedBar` API.
All effects run synchronously and respect a ``running`` flag that can be
cleared from another thread to stop the effect gracefully.
"""

from __future__ import annotations

import logging
import math
import random
import threading
import time

from raspbot.actuators.led_bar import LedBar
from raspbot.types import LedColor, NUM_LEDS

logger = logging.getLogger(__name__)


class LightEffects:
    """Animated LED effects controller.

    Parameters
    ----------
    led_bar:
        The :class:`~raspbot.actuators.led_bar.LedBar` instance to drive.
    """

    def __init__(self, led_bar: LedBar) -> None:
        self._bar = led_bar
        self._running = False
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def stop(self) -> None:
        """Request the currently running effect to stop after its next cycle."""
        with self._lock:
            self._running = False

    def off(self) -> None:
        """Turn off all LEDs immediately."""
        self._bar.off_all()

    # ------------------------------------------------------------------
    # Effects
    # ------------------------------------------------------------------

    def river(self, duration: float = 10.0, speed: float = 0.05) -> None:
        """Sequential chase-light cycling through all 7 colours.

        Parameters
        ----------
        duration:
            How long (seconds) to run the effect.
        speed:
            Delay (seconds) between each LED step.
        """
        colors = list(LedColor)
        color_idx = 0
        end = time.time() + duration
        with self._lock:
            self._running = True
        try:
            while self._running and time.time() < end:
                for i in range(NUM_LEDS - 2):
                    if not self._running:
                        break
                    for offset in range(3):
                        self._bar.set_one(i + offset, colors[color_idx])
                    time.sleep(speed)
                    self._bar.off_all()
                    time.sleep(speed)
                color_idx = (color_idx + 1) % len(colors)
        finally:
            self._bar.off_all()
            with self._lock:
                self._running = False

    def breathing(
        self,
        color: LedColor = LedColor.BLUE,
        duration: float = 10.0,
        speed: float = 0.01,
    ) -> None:
        """Fade all LEDs in and out on a single colour.

        Parameters
        ----------
        color:
            Which :class:`~raspbot.types.LedColor` to breathe.
        duration:
            How long (seconds) to run the effect.
        speed:
            Delay (seconds) between brightness steps.
        """
        _COLOR_MAP = {
            LedColor.RED:    (1, 0, 0),
            LedColor.GREEN:  (0, 1, 0),
            LedColor.BLUE:   (0, 0, 1),
            LedColor.YELLOW: (1, 1, 0),
            LedColor.PURPLE: (1, 0, 1),
            LedColor.CYAN:   (0, 1, 1),
            LedColor.WHITE:  (1, 1, 1),
        }
        factors = _COLOR_MAP.get(color, (1, 1, 1))
        brightness = 0
        direction = 1
        end = time.time() + duration
        with self._lock:
            self._running = True
        try:
            while self._running and time.time() < end:
                r = int(brightness * factors[0])
                g = int(brightness * factors[1])
                b = int(brightness * factors[2])
                self._bar.set_brightness_all(r, g, b)
                time.sleep(speed)
                brightness += 2 * direction
                if brightness >= 255:
                    brightness = 255
                    direction = -1
                elif brightness <= 0:
                    brightness = 0
                    direction = 1
        finally:
            self._bar.off_all()
            with self._lock:
                self._running = False

    def random_running(self, duration: float = 10.0, speed: float = 0.05) -> None:
        """Randomly colour each LED every tick.

        Parameters
        ----------
        duration:
            How long (seconds) to run the effect.
        speed:
            Delay (seconds) between frames.
        """
        colors = list(LedColor)
        end = time.time() + duration
        with self._lock:
            self._running = True
        try:
            while self._running and time.time() < end:
                for i in range(NUM_LEDS):
                    self._bar.set_one(i, random.choice(colors))
                time.sleep(speed)
        finally:
            self._bar.off_all()
            with self._lock:
                self._running = False

    def starlight(self, duration: float = 10.0, speed: float = 0.1) -> None:
        """Random subset of LEDs lit, cycling through colours.

        Parameters
        ----------
        duration:
            How long (seconds) to run the effect.
        speed:
            Delay (seconds) between frames.
        """
        colors = list(LedColor)
        end = time.time() + duration
        with self._lock:
            self._running = True
        try:
            for color in colors:
                if not self._running or time.time() >= end:
                    break
                cycle_end = time.time() + 1.0
                while self._running and time.time() < cycle_end:
                    self._bar.off_all()
                    k = random.randint(1, NUM_LEDS // 2)
                    lit = random.sample(range(NUM_LEDS), k=k)
                    for idx in lit:
                        self._bar.set_one(idx, color)
                    time.sleep(speed)
        finally:
            self._bar.off_all()
            with self._lock:
                self._running = False

    def gradient(self, duration: float = 10.0, speed: float = 0.02) -> None:
        """Sequential fill with a random RGB colour, then reverse-fill.

        Parameters
        ----------
        duration:
            How long (seconds) to run the effect.
        speed:
            Delay (seconds) between each LED step.
        """
        end = time.time() + duration
        with self._lock:
            self._running = True
        try:
            while self._running and time.time() < end:
                r, g, b = self._random_rgb()
                for i in range(NUM_LEDS):
                    if not self._running:
                        break
                    self._bar.set_brightness_one(i, r, g, b)
                    time.sleep(speed)
                for i in range(NUM_LEDS - 1, -1, -1):
                    if not self._running:
                        break
                    self._bar.set_brightness_one(i, 0, 0, 0)
                    time.sleep(speed)
        finally:
            self._bar.off_all()
            with self._lock:
                self._running = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _random_rgb() -> tuple[int, int, int]:
        """Generate a random RGB triple where at most two channels are non-zero."""
        channels = [random.randint(40, 255) for _ in range(3)]
        # Zero out one channel to keep colours saturated
        channels[random.randint(0, 2)] = 0
        return channels[0], channels[1], channels[2]
