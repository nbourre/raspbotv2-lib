"""
03_buzzer.py - Piezo buzzer control (non-blocking tick pattern)

Demonstrates Buzzer methods:
  - on() / off()       raw immediate hardware control
  - beep()             schedule a single non-blocking beep
  - pattern()          schedule a repeated non-blocking beep pattern
  - update(ct)         advance the state machine (call every loop iteration)
  - is_active          True while a beep or pattern is in progress

All timed operations return immediately.  The main loop calls update(ct)
to drive on/off transitions without ever sleeping.

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot

LOOP_SLEEP = 0.001  # 1 ms loop tick

with Robot() as bot:
    # ------------------------------------------------------------------
    # Raw on / off
    # ------------------------------------------------------------------

    print("Buzzer on for 0.5 s (raw) ...")
    bot.buzzer.on()
    time.sleep(0.5)          # time.sleep is acceptable in setup/demo code
    bot.buzzer.off()
    time.sleep(0.3)

    # ------------------------------------------------------------------
    # Single beep via state machine
    # ------------------------------------------------------------------

    print("Scheduling 200 ms beep ...")
    bot.buzzer.beep(duration=0.2)

    while bot.buzzer.is_active:
        bot.buzzer.update(time.monotonic())
        time.sleep(LOOP_SLEEP)

    time.sleep(0.3)

    # ------------------------------------------------------------------
    # Repeated pattern via state machine
    # ------------------------------------------------------------------

    print("Scheduling SOS dots (3 short beeps) ...")
    bot.buzzer.pattern(on_time=0.1, off_time=0.1, count=3)

    while bot.buzzer.is_active:
        bot.buzzer.update(time.monotonic())
        time.sleep(LOOP_SLEEP)

    time.sleep(0.3)

    print("Scheduling SOS dashes (3 long beeps) ...")
    bot.buzzer.pattern(on_time=0.5, off_time=0.2, count=3)

    while bot.buzzer.is_active:
        bot.buzzer.update(time.monotonic())
        time.sleep(LOOP_SLEEP)

print("Done.")
