"""
06_ultrasonic.py - Ultrasonic distance sensor

Demonstrates UltrasonicSensor methods:
  - enable() / disable()   power the sensor on/off
  - read_mm()              distance in millimetres
  - read_cm()              distance in centimetres
  - context manager        auto-enables on enter, disables on exit

The sensor must be enabled before reading.  Use the context manager
(or call enable() explicitly) to avoid getting stale zeroes.

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot

with Robot() as bot:
    # ------------------------------------------------------------------
    # Context manager: enable on entry, disable on exit
    # ------------------------------------------------------------------

    print("Reading distance for 5 s (context manager) ...")
    with bot.ultrasonic:
        end = time.monotonic() + 5.0
        while time.monotonic() < end:
            mm = bot.ultrasonic.read_mm()
            cm = bot.ultrasonic.read_cm()
            print(f"  {mm:5d} mm  /  {cm:6.1f} cm")
            time.sleep(0.2)

    # ------------------------------------------------------------------
    # Manual enable / disable
    # ------------------------------------------------------------------

    print("\nManual enable/disable ...")
    bot.ultrasonic.enable()
    time.sleep(0.1)  # brief settle after enable

    for _ in range(5):
        print(f"  {bot.ultrasonic.read_mm()} mm")
        time.sleep(0.2)

    bot.ultrasonic.disable()

print("Done.")
