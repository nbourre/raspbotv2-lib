"""
09_button.py - KEY1 tactile button

Demonstrates Button.is_pressed():
  - Polls the KEY1 button state (no interrupts, no background thread).
  - Returns True while held down, False when released.

Run on Raspberry Pi with the Raspbot V2 powered on.
Press and hold the KEY1 button on the robot to see the output change.
"""

import time

from raspbot import Robot

# Button is also exported from the top-level package for convenience:
#   from raspbot import Button

with Robot() as bot:
    # ------------------------------------------------------------------
    # Simple polling loop
    # ------------------------------------------------------------------

    print("Polling KEY1 for 10 s -- press the button to see it register.")
    print("Ctrl+C to stop early.")

    was_pressed = False
    end = time.monotonic() + 10.0

    try:
        while time.monotonic() < end:
            pressed = bot.button.is_pressed()

            if pressed and not was_pressed:
                print("  Button PRESSED")
            elif not pressed and was_pressed:
                print("  Button released")

            was_pressed = pressed
            time.sleep(0.05)  # 50 ms poll interval -- fine for human input
    except KeyboardInterrupt:
        pass

    # ------------------------------------------------------------------
    # Wait for a single press (blocking helper pattern)
    # ------------------------------------------------------------------

    print("\nWaiting for a single button press (up to 10 s) ...")
    deadline = time.monotonic() + 10.0
    detected = False

    try:
        while time.monotonic() < deadline:
            if bot.button.is_pressed():
                print("  Got it!")
                detected = True
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass

    if not detected:
        print("  (timed out -- button was not pressed)")

print("Done.")
