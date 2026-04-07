"""
15_buzzer_effects_tick.py - Cooperative tick loop with Buzzer and LightEffects

Shows how to drive Buzzer and LightEffects together in a single main loop
without any blocking calls inside the library.

The pattern mirrors the Arduino OneButton / millis() approach:
  ct = time.monotonic()
  bot.buzzer.update(ct)
  bot.light_effects.update(ct)

Everything is driven by the same ct value, so all state machines stay in sync.

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot
from raspbot.types import LedColor
from raspbot.utils.task import Task

LOOP_SLEEP = 0.001      # 1 ms loop tick -- keeps CPU usage low


with Robot() as bot:
    # ------------------------------------------------------------------
    # Start a breathing blue effect immediately
    # ------------------------------------------------------------------

    bot.light_effects.start_breathing(LedColor.BLUE, speed=0.01)

    # ------------------------------------------------------------------
    # Use Task to fire a 3-beep alert pattern every 5 seconds
    # ------------------------------------------------------------------

    def alert(ct: float) -> None:
        bot.buzzer.pattern(on_time=0.05, off_time=0.05, count=3)

    task_alert = Task(alert, rate=5.0)

    # ------------------------------------------------------------------
    # Use Task to rotate through effects every 8 seconds
    # ------------------------------------------------------------------

    effects_cycle = [
        lambda: bot.light_effects.start_river(speed=0.05),
        lambda: bot.light_effects.start_breathing(LedColor.GREEN, speed=0.01),
        lambda: bot.light_effects.start_starlight(speed=0.1),
        lambda: bot.light_effects.start_random_running(speed=0.05),
        lambda: bot.light_effects.start_gradient(speed=0.02),
    ]
    effect_idx = [0]

    def rotate_effect(ct: float) -> None:
        effects_cycle[effect_idx[0]]()
        effect_idx[0] = (effect_idx[0] + 1) % len(effects_cycle)

    task_effects = Task(rotate_effect, rate=8.0, run_immediately=False)

    # ------------------------------------------------------------------
    # Main loop -- runs for 40 seconds then exits cleanly
    # ------------------------------------------------------------------

    print("Running for 40 s.  Buzzer beeps every 5 s, effects rotate every 8 s.")
    end = time.monotonic() + 40.0

    while time.monotonic() < end:
        ct = time.monotonic()

        bot.buzzer.update(ct)
        bot.light_effects.update(ct)
        task_alert(ct)
        task_effects(ct)

        time.sleep(LOOP_SLEEP)

    # ------------------------------------------------------------------
    # Clean up
    # ------------------------------------------------------------------

    bot.light_effects.stop()
    bot.buzzer.off()

print("Done.")
