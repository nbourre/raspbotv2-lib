"""
05_led_effects.py - Animated LED effects (non-blocking tick pattern)

Demonstrates LightEffects methods:
  - start_river()          sequential chase light
  - start_breathing()      smooth fade in/out on a single colour
  - start_random_running() random colours on every LED each tick
  - start_starlight()      random subsets of LEDs lit per colour
  - start_gradient()       sequential fill with random RGB, then reverse-fill
  - update(ct)             advance the animation (call every loop iteration)
  - stop() / off()         cancel the current effect and turn off all LEDs
  - is_active              True while an effect is running

All start_* methods return immediately.  The main loop calls update(ct)
to drive animation frames without ever sleeping inside the library.

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot
from raspbot.types import LedColor

EFFECT_DURATION = 3.0   # seconds to run each effect
LOOP_SLEEP = 0.001      # 1 ms loop tick


def run_effect_for(bot: "Robot", seconds: float) -> None:  # type: ignore[name-defined]
    """Drive update() for *seconds* then stop."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        bot.light_effects.update(time.monotonic())
        time.sleep(LOOP_SLEEP)
    bot.light_effects.stop()
    time.sleep(0.3)


with Robot() as bot:
    effects = bot.light_effects

    # ------------------------------------------------------------------
    # river -- chasing coloured pixels across the bar
    # ------------------------------------------------------------------

    print("Effect: river (3 s) ...")
    effects.start_river(speed=0.05)
    run_effect_for(bot, EFFECT_DURATION)

    # ------------------------------------------------------------------
    # breathing -- smooth fade on a single colour
    # ------------------------------------------------------------------

    print("Effect: breathing blue (3 s) ...")
    effects.start_breathing(color=LedColor.BLUE, speed=0.01)
    run_effect_for(bot, EFFECT_DURATION)

    # ------------------------------------------------------------------
    # random_running -- random colours on all LEDs every tick
    # ------------------------------------------------------------------

    print("Effect: random_running (3 s) ...")
    effects.start_random_running(speed=0.05)
    run_effect_for(bot, EFFECT_DURATION)

    # ------------------------------------------------------------------
    # starlight -- random lit subset, cycling colours
    # ------------------------------------------------------------------

    print("Effect: starlight (3 s) ...")
    effects.start_starlight(speed=0.1)
    run_effect_for(bot, EFFECT_DURATION)

    # ------------------------------------------------------------------
    # gradient -- sequential fill then reverse with random RGB colour
    # ------------------------------------------------------------------

    print("Effect: gradient (3 s) ...")
    effects.start_gradient(speed=0.04)
    run_effect_for(bot, EFFECT_DURATION)

    # ------------------------------------------------------------------
    # off() -- immediately blank the LED bar
    # ------------------------------------------------------------------

    effects.off()

print("Done.")
