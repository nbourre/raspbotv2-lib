"""
07_line_tracker.py - 4-channel IR line tracker

Demonstrates LineTracker and LineState:
  - read()           returns a LineState snapshot
  - LineState.x1-x4  per-channel booleans (True = dark/on-line)
  - LineState.raw    raw byte from the sensor
  - LineState.on_line    True if any channel sees a line
  - LineState.centered   True if both centre channels see a line

Sensor channel layout (top-down view):
  x1  x2  x3  x4
  L   CL  CR  R      (left / centre-left / centre-right / right)

Run on Raspberry Pi with the Raspbot V2 powered on.
Place the robot over a dark line on a light surface to see live readings.
"""

import time

from raspbot import Robot

with Robot() as bot:
    print("Reading line tracker for 10 s -- Ctrl+C to stop early.")
    print(f"{'x1':>4} {'x2':>4} {'x3':>4} {'x4':>4}  {'raw':>5}  on_line  centered")
    print("-" * 52)

    end = time.monotonic() + 10.0
    try:
        while time.monotonic() < end:
            state = bot.line_tracker.read()

            # Boolean channels -- True when over a dark line
            x1 = "1" if state.x1 else "."
            x2 = "1" if state.x2 else "."
            x3 = "1" if state.x3 else "."
            x4 = "1" if state.x4 else "."

            print(
                f"   {x1}    {x2}    {x3}    {x4}   "
                f"{state.raw:#04x}    "
                f"{'yes' if state.on_line else 'no ':3}      "
                f"{'yes' if state.centered else 'no'}"
            )
            time.sleep(0.15)
    except KeyboardInterrupt:
        pass

print("Done.")
