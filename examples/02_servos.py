"""
02_servos.py - Pan/tilt servo control

Demonstrates Servo and ServoPair methods:
  - set_angle()   move to a specific angle
  - home()        return to centre / rest position
  - max_angle     read the hardware limit for a channel

Hardware limits:
  - PAN  (servo 1): 0-180 degrees
  - TILT (servo 2): 0-110 degrees  (enforced by the library)

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot

with Robot() as bot:
    # ------------------------------------------------------------------
    # ServoPair.home() -- move both servos to their rest positions
    # ------------------------------------------------------------------

    print("Homing both servos ...")
    bot.servos.home()  # pan -> 90 deg, tilt -> 25 deg
    time.sleep(1)

    # ------------------------------------------------------------------
    # Individual servo control via bot.servos.pan / bot.servos.tilt
    # ------------------------------------------------------------------

    print(f"PAN  max angle: {bot.servos.pan.max_angle} deg")
    print(f"TILT max angle: {bot.servos.tilt.max_angle} deg")

    # Sweep pan left to right
    print("Sweeping pan 0 -> 180 -> 90 ...")
    for angle in (0, 45, 90, 135, 180, 90):
        bot.servos.pan.set_angle(angle)
        time.sleep(0.4)

    # Tilt up and down (library clamps anything above 110 automatically)
    print("Tilting 0 -> 110 -> 25 ...")
    for angle in (0, 55, 110, 25):
        bot.servos.tilt.set_angle(angle)
        time.sleep(0.4)

    # ------------------------------------------------------------------
    # Passing a value above the hardware limit is silently clamped
    # ------------------------------------------------------------------

    print("Requesting tilt 180 (will be clamped to 110) ...")
    bot.servos.tilt.set_angle(180)
    time.sleep(0.5)

    # Return both to home
    bot.servos.home()

print("Done.")
