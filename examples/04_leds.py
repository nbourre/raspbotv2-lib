"""
04_leds.py - WS2812 RGB LED bar control

Demonstrates LedBar methods:
  - set_all()            set every LED to a predefined colour
  - set_one()            set a single LED by index
  - off_all() / off_one() turn off all or one LED
  - set_brightness_all() set raw RGB values for all LEDs simultaneously
  - set_brightness_one() set raw RGB values for a single LED
  - count                number of LEDs on the bar (14)

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot
from raspbot.types import LedColor

with Robot() as bot:
    print(f"LED bar has {bot.leds.count} LEDs")

    # ------------------------------------------------------------------
    # set_all() -- predefined colour codes
    # ------------------------------------------------------------------

    for color in LedColor:
        print(f"All LEDs -> {color.name}")
        bot.leds.set_all(color)
        time.sleep(0.4)

    bot.leds.off_all()
    time.sleep(0.3)

    # ------------------------------------------------------------------
    # set_one() -- individual LED control
    # ------------------------------------------------------------------

    print("Lighting LEDs one by one ...")
    for i in range(bot.leds.count):
        color = LedColor(i % len(LedColor))
        bot.leds.set_one(i, color)
        time.sleep(0.1)

    time.sleep(0.5)
    bot.leds.off_all()
    time.sleep(0.3)

    # off_one() -- turn off a single LED while leaving the rest on
    bot.leds.set_all(LedColor.WHITE)
    time.sleep(0.5)
    print("Turning off every other LED ...")
    for i in range(0, bot.leds.count, 2):
        bot.leds.off_one(i)
    time.sleep(0.8)
    bot.leds.off_all()
    time.sleep(0.3)

    # ------------------------------------------------------------------
    # set_brightness_all() -- raw RGB brightness (0-255 per channel)
    # ------------------------------------------------------------------

    print("Raw RGB brightness: red fade-in ...")
    for level in range(0, 256, 8):
        bot.leds.set_brightness_all(level, 0, 0)
        time.sleep(0.02)

    print("Raw RGB brightness: fade out ...")
    for level in range(255, -1, -8):
        bot.leds.set_brightness_all(level, 0, 0)
        time.sleep(0.02)

    # ------------------------------------------------------------------
    # set_brightness_one() -- raw RGB on a single LED
    # ------------------------------------------------------------------

    print("Raw RGB brightness on LED 0: teal ...")
    bot.leds.set_brightness_one(0, r=0, g=180, b=180)
    time.sleep(0.8)

    bot.leds.off_all()

print("Done.")
