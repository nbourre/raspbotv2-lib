"""
05_led_effects.py - Animated LED effects

Demonstrates LightEffects methods (all run synchronously):
  - river()          sequential chase light
  - breathing()      smooth fade in/out on a single colour
  - random_running() random colours on every LED each tick
  - starlight()      random subsets of LEDs lit per colour
  - gradient()       sequential fill with random RGB, then reverse-fill
  - stop()           thread-safe stop request (useful when running in a thread)
  - off()            immediately blank all LEDs

All effects accept duration (seconds) and speed (seconds per tick).

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot
from raspbot.types import LedColor, LightEffect

with Robot() as bot:
    effects = bot.light_effects

    # ------------------------------------------------------------------
    # river -- chasing coloured pixels across the bar
    # ------------------------------------------------------------------

    print(f"Effect: {LightEffect.RIVER} (3 s) ...")
    effects.river(duration=3.0, speed=0.05)

    time.sleep(0.3)

    # ------------------------------------------------------------------
    # breathing -- smooth fade on a single colour
    # ------------------------------------------------------------------

    print(f"Effect: {LightEffect.BREATHING} (3 s, blue) ...")
    effects.breathing(color=LedColor.BLUE, duration=3.0, speed=0.01)

    time.sleep(0.3)

    # ------------------------------------------------------------------
    # random_running -- random colours on all LEDs every tick
    # ------------------------------------------------------------------

    print(f"Effect: {LightEffect.RANDOM} (3 s) ...")
    effects.random_running(duration=3.0, speed=0.05)

    time.sleep(0.3)

    # ------------------------------------------------------------------
    # starlight -- random lit subset, cycling colours
    # ------------------------------------------------------------------

    print(f"Effect: {LightEffect.STARLIGHT} (3 s) ...")
    effects.starlight(duration=3.0, speed=0.1)

    time.sleep(0.3)

    # ------------------------------------------------------------------
    # gradient -- sequential fill then reverse with random RGB colour
    # ------------------------------------------------------------------

    print(f"Effect: {LightEffect.GRADIENT} (3 s) ...")
    effects.gradient(duration=3.0, speed=0.04)

    # ------------------------------------------------------------------
    # off() -- immediately blank the LED bar
    # ------------------------------------------------------------------

    effects.off()

print("Done.")
