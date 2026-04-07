"""
03_buzzer.py - Piezo buzzer control

Demonstrates Buzzer methods:
  - on() / off()       raw on/off control
  - beep()             single timed beep
  - pattern()          repeated beep pattern

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot

with Robot() as bot:
    # ------------------------------------------------------------------
    # Raw on / off
    # ------------------------------------------------------------------

    print("Buzzer on for 0.5 s ...")
    bot.buzzer.on()
    time.sleep(0.5)
    bot.buzzer.off()
    time.sleep(0.5)

    # ------------------------------------------------------------------
    # beep() -- convenience wrapper that turns on then off automatically
    # ------------------------------------------------------------------

    print("Single beep (0.2 s) ...")
    bot.buzzer.beep(duration=0.2)
    time.sleep(0.3)

    print("Long beep (1 s) ...")
    bot.buzzer.beep(duration=1.0)
    time.sleep(0.3)

    # ------------------------------------------------------------------
    # pattern() -- repeated beep-pause sequence
    # ------------------------------------------------------------------

    print("3 short beeps (SOS-style dots) ...")
    bot.buzzer.pattern(on_time=0.1, off_time=0.1, count=3)
    time.sleep(0.3)

    print("3 long beeps (SOS-style dashes) ...")
    bot.buzzer.pattern(on_time=0.5, off_time=0.2, count=3)

print("Done.")
