"""
LED light animation effects engine.

Provides animated visual effects built on top of
:class:`~raspbot.actuators.led_bar.LedBar`.

All effects are non-blocking.  Set the desired effect with one of the
``start_*`` methods, then call :meth:`update` on every main-loop iteration
to advance the animation by one frame.  Call :meth:`stop` at any time to
cancel the current effect and turn off all LEDs.

Usage::

    import time
    from raspbot import RaspBot
    from raspbot.types import LedColor

    bot = RaspBot()
    bot.light_effects.start_breathing(LedColor.BLUE, speed=0.01)

    while True:
        ct = time.monotonic()
        bot.light_effects.update(ct)
        # ... rest of loop
"""

from __future__ import annotations

import logging
import random
import time
from enum import Enum, auto

from raspbot.actuators.led_bar import LedBar
from raspbot.types import NUM_LEDS, LedColor

logger = logging.getLogger(__name__)

# Per-colour RGB scale factors used by the breathing effect
_BREATHING_MAP: dict[LedColor, tuple[int, int, int]] = {
    LedColor.RED:    (1, 0, 0),
    LedColor.GREEN:  (0, 1, 0),
    LedColor.BLUE:   (0, 0, 1),
    LedColor.YELLOW: (1, 1, 0),
    LedColor.PURPLE: (1, 0, 1),
    LedColor.CYAN:   (0, 1, 1),
    LedColor.WHITE:  (1, 1, 1),
}


class _Effect(Enum):
    NONE           = auto()
    RIVER          = auto()
    BREATHING      = auto()
    RANDOM_RUNNING = auto()
    STARLIGHT      = auto()
    GRADIENT       = auto()


class LightEffects:
    """Animated LED effects controller.

    Parameters
    ----------
    led_bar:
        The :class:`~raspbot.actuators.led_bar.LedBar` instance to drive.
    """

    def __init__(self, led_bar: LedBar) -> None:
        self._bar = led_bar
        self._effect: _Effect = _Effect.NONE
        self._next_frame: float = 0.0   # monotonic deadline for next frame

        # --- per-effect state ---
        # river
        self._river_colors: list[LedColor] = []
        self._river_color_idx: int = 0
        self._river_led_idx: int = 0
        self._river_show: bool = True   # True=show group, False=blank gap

        # breathing
        self._breath_factors: tuple[int, int, int] = (1, 1, 1)
        self._breath_brightness: int = 0
        self._breath_direction: int = 1

        # random_running  (stateless per-frame, no extra fields needed)

        # starlight
        self._star_colors: list[LedColor] = []
        self._star_color_idx: int = 0
        self._star_cycle_end: float = 0.0

        # gradient
        self._grad_r: int = 0
        self._grad_g: int = 0
        self._grad_b: int = 0
        self._grad_idx: int = 0
        self._grad_filling: bool = True  # True=filling in, False=erasing

        # speed / frame interval (seconds)
        self._speed: float = 0.05

    # ------------------------------------------------------------------
    # Effect starters
    # ------------------------------------------------------------------

    def start_river(self, speed: float = 0.05) -> None:
        """Start the sequential chase-light effect.

        Each frame advances a 3-LED window one step, cycling through all 7
        colours.

        Parameters
        ----------
        speed:
            Seconds between each LED step.
        """
        self._effect = _Effect.RIVER
        self._speed = speed
        self._river_colors = list(LedColor)
        self._river_color_idx = 0
        self._river_led_idx = 0
        self._river_show = True
        self._next_frame = 0.0

    def start_breathing(
        self,
        color: LedColor = LedColor.BLUE,
        speed: float = 0.01,
    ) -> None:
        """Start the breathing (fade in/out) effect on a single colour.

        Parameters
        ----------
        color:
            Which :class:`~raspbot.types.LedColor` to breathe.
        speed:
            Seconds between brightness steps.
        """
        self._effect = _Effect.BREATHING
        self._speed = speed
        self._breath_factors = _BREATHING_MAP.get(color, (1, 1, 1))
        self._breath_brightness = 0
        self._breath_direction = 1
        self._next_frame = 0.0

    def start_random_running(self, speed: float = 0.05) -> None:
        """Start the random-colour-per-LED effect.

        Each frame assigns a random :class:`~raspbot.types.LedColor` to
        every LED.

        Parameters
        ----------
        speed:
            Seconds between frames.
        """
        self._effect = _Effect.RANDOM_RUNNING
        self._speed = speed
        self._next_frame = 0.0

    def start_starlight(self, speed: float = 0.1) -> None:
        """Start the starlight (random subset) effect.

        A random subset of LEDs is lit each frame.  The active colour
        cycles through all 7 colours, spending about one second on each.

        Parameters
        ----------
        speed:
            Seconds between frames.
        """
        self._effect = _Effect.STARLIGHT
        self._speed = speed
        self._star_colors = list(LedColor)
        self._star_color_idx = 0
        self._star_cycle_end = 0.0   # will be set on first update()
        self._next_frame = 0.0

    def start_gradient(self, speed: float = 0.02) -> None:
        """Start the gradient fill/erase effect.

        LEDs are filled one by one with a random saturated colour, then
        erased one by one, repeating indefinitely.

        Parameters
        ----------
        speed:
            Seconds between each LED step.
        """
        self._effect = _Effect.GRADIENT
        self._speed = speed
        self._grad_r, self._grad_g, self._grad_b = self._random_rgb()
        self._grad_idx = 0
        self._grad_filling = True
        self._next_frame = 0.0

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def stop(self) -> None:
        """Cancel the current effect and turn off all LEDs."""
        self._effect = _Effect.NONE
        self._bar.off_all()

    def off(self) -> None:
        """Turn off all LEDs immediately (alias for :meth:`stop`)."""
        self.stop()

    # ------------------------------------------------------------------
    # Cooperative tick
    # ------------------------------------------------------------------

    def update(self, ct: float | None = None) -> None:
        """Advance the current effect by one frame if enough time has elapsed.

        Call this on every main-loop iteration.  When called with no
        argument it reads the current time via :func:`time.monotonic`
        automatically, mirroring the Arduino ``millis()`` pattern.

        Parameters
        ----------
        ct:
            Current time in seconds.  Defaults to ``time.monotonic()``
            when omitted, so both calling styles are valid::

                bot.light_effects.update()     # autonomous
                bot.light_effects.update(ct)   # shared ct from the loop
        """
        if ct is None:
            ct = time.monotonic()
        if self._effect is _Effect.NONE:
            return
        if ct < self._next_frame:
            return
        self._next_frame = ct + self._speed

        if self._effect is _Effect.RIVER:
            self._tick_river()
        elif self._effect is _Effect.BREATHING:
            self._tick_breathing()
        elif self._effect is _Effect.RANDOM_RUNNING:
            self._tick_random_running()
        elif self._effect is _Effect.STARLIGHT:
            self._tick_starlight(ct)
        elif self._effect is _Effect.GRADIENT:
            self._tick_gradient()

    # ------------------------------------------------------------------
    # State query
    # ------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """``True`` while an effect is running."""
        return self._effect is not _Effect.NONE

    # ------------------------------------------------------------------
    # Per-effect tick helpers
    # ------------------------------------------------------------------

    def _tick_river(self) -> None:
        colors = self._river_colors
        if self._river_show:
            # Light the current 3-LED group
            for offset in range(3):
                idx = self._river_led_idx + offset
                if idx < NUM_LEDS:
                    self._bar.set_one(idx, colors[self._river_color_idx])
            self._river_show = False
        else:
            # Blank gap
            self._bar.off_all()
            self._river_show = True
            self._river_led_idx += 1
            if self._river_led_idx >= NUM_LEDS - 2:
                self._river_led_idx = 0
                self._river_color_idx = (self._river_color_idx + 1) % len(colors)

    def _tick_breathing(self) -> None:
        f = self._breath_factors
        r = int(self._breath_brightness * f[0])
        g = int(self._breath_brightness * f[1])
        b = int(self._breath_brightness * f[2])
        self._bar.set_brightness_all(r, g, b)
        self._breath_brightness += 2 * self._breath_direction
        if self._breath_brightness >= 255:
            self._breath_brightness = 255
            self._breath_direction = -1
        elif self._breath_brightness <= 0:
            self._breath_brightness = 0
            self._breath_direction = 1

    def _tick_random_running(self) -> None:
        colors = list(LedColor)
        for i in range(NUM_LEDS):
            self._bar.set_one(i, random.choice(colors))

    def _tick_starlight(self, ct: float) -> None:
        colors = self._star_colors
        # Initialise cycle end on the very first tick
        if self._star_cycle_end == 0.0:
            self._star_cycle_end = ct + 1.0

        if ct >= self._star_cycle_end:
            # Advance to the next colour
            self._star_color_idx = (self._star_color_idx + 1) % len(colors)
            self._star_cycle_end = ct + 1.0

        color = colors[self._star_color_idx]
        self._bar.off_all()
        k = random.randint(1, NUM_LEDS // 2)
        lit = random.sample(range(NUM_LEDS), k=k)
        for idx in lit:
            self._bar.set_one(idx, color)

    def _tick_gradient(self) -> None:
        if self._grad_filling:
            self._bar.set_brightness_one(
                self._grad_idx, self._grad_r, self._grad_g, self._grad_b
            )
            self._grad_idx += 1
            if self._grad_idx >= NUM_LEDS:
                self._grad_idx = NUM_LEDS - 1
                self._grad_filling = False
        else:
            self._bar.set_brightness_one(self._grad_idx, 0, 0, 0)
            self._grad_idx -= 1
            if self._grad_idx < 0:
                # Start a new fill cycle with a fresh colour
                self._grad_r, self._grad_g, self._grad_b = self._random_rgb()
                self._grad_idx = 0
                self._grad_filling = True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _random_rgb() -> tuple[int, int, int]:
        """Return a random saturated RGB triple (one channel is always zero)."""
        channels = [random.randint(40, 255) for _ in range(3)]
        channels[random.randint(0, 2)] = 0
        return channels[0], channels[1], channels[2]
