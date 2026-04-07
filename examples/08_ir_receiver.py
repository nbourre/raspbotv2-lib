"""
08_ir_receiver.py - IR remote control receiver

Demonstrates IRReceiver methods:
  - enable() / disable()   activate/deactivate the receiver
  - read_keycode()         return the latest key code (int) or None if idle
  - context manager        auto-enables and auto-disables

Point any NEC-compatible IR remote at the robot's receiver and press
buttons to see the key codes printed.

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot

with Robot() as bot:
    # ------------------------------------------------------------------
    # Context manager (recommended): auto-enable / auto-disable
    # ------------------------------------------------------------------

    print("Waiting for IR key presses for 15 s -- Ctrl+C to stop early.")
    print("(Point your remote at the robot and press buttons.)")

    with bot.ir:
        last_code: int | None = None
        end = time.monotonic() + 15.0
        try:
            while time.monotonic() < end:
                code = bot.ir.read_keycode()
                if code is not None and code != last_code:
                    print(f"  Key code received: 0x{code:02X}  ({code})")
                    last_code = code
                elif code is None:
                    last_code = None  # reset so the same key fires again
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass

    # ------------------------------------------------------------------
    # Manual enable / disable
    # ------------------------------------------------------------------

    print("\nManual enable/disable (3 s) ...")
    bot.ir.enable()
    end = time.monotonic() + 3.0
    try:
        while time.monotonic() < end:
            code = bot.ir.read_keycode()
            if code is not None:
                print(f"  Code: 0x{code:02X}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        bot.ir.disable()

print("Done.")
