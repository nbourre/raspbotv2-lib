"""
13_robot_complete.py - Complete robot demo

Combines all subsystems into a single non-blocking event loop using Task.

Behaviour (runs for ~20 s then stops):
  - Every 0.1 s: read the ultrasonic sensor
  - Every 0.1 s: read the line tracker
  - Every 0.2 s: read the button; beep once if pressed
  - Every 1.0 s: print a status summary to the terminal
  - Every 2.0 s: cycle LEDs through colours
  - If obstacle < 20 cm: stop motors and tilt the camera servo down
  - If no obstacle and on a line: follow the line with proportional steering
  - If no obstacle and no line: drive forward at a moderate speed

Requires:
    pip install raspbot

Optional (uncomment OLED / camera sections):
    pip install "raspbot[oled]" "raspbot[camera]"

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

from __future__ import annotations

import time

from raspbot import Robot, Task
from raspbot.sensors.line_tracker import LineState
from raspbot.types import LedColor

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

distance_mm: int = 9999
line_state: LineState | None = None
led_index: int = 0
SAFE_DISTANCE_MM = 200  # stop if obstacle is closer than this

COLORS = list(LedColor)

# ---------------------------------------------------------------------------
# Task functions -- each receives current_time but uses shared state
# ---------------------------------------------------------------------------


def read_ultrasonic(ct: float) -> None:
    global distance_mm
    distance_mm = bot.ultrasonic.read_mm()


def read_line(ct: float) -> None:
    global line_state
    line_state = bot.line_tracker.read()


def check_button(ct: float) -> None:
    if bot.button.is_pressed():
        bot.buzzer.beep(0.05)


def cycle_leds(ct: float) -> None:
    global led_index
    bot.leds.set_all(COLORS[led_index % len(COLORS)])
    led_index += 1


def drive(ct: float) -> None:
    """Simple obstacle-avoidance + line-following controller."""
    if distance_mm < SAFE_DISTANCE_MM:
        # Obstacle too close -- stop and look down
        bot.motors.stop()
        bot.servos.tilt.set_angle(0)
        return

    bot.servos.tilt.set_angle(25)  # level gaze

    if line_state is None or not line_state.on_line:
        # No line detected -- drive straight
        bot.motors.forward(speed=120)
        return

    # Proportional line-following using sensor pattern
    ls = line_state
    if ls.centered:
        bot.motors.forward(speed=120)
    elif ls.x1 and not ls.x4:
        # Drifting right -- steer left
        bot.motors.turn_left(speed=100)
    elif ls.x4 and not ls.x1:
        # Drifting left -- steer right
        bot.motors.turn_right(speed=100)
    else:
        bot.motors.forward(speed=100)


def print_status(ct: float) -> None:
    ls_str = str(line_state) if line_state else "none"
    print(f"t={ct:6.1f}s  dist={distance_mm:5d}mm  line={ls_str}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

with Robot() as bot:
    # Enable the ultrasonic sensor once at the start
    bot.ultrasonic.enable()
    bot.servos.home()

    # Build the task schedule
    tasks = [
        Task(read_ultrasonic, rate=0.10),
        Task(read_line, rate=0.10),
        Task(check_button, rate=0.20),
        Task(drive, rate=0.10),
        Task(cycle_leds, rate=2.00),
        Task(print_status, rate=1.00),
    ]

    print("Running for 20 s -- Ctrl+C to stop early.")
    end = time.monotonic() + 20.0

    try:
        while time.monotonic() < end:
            ct = time.monotonic()
            for task in tasks:
                task(ct)
            time.sleep(0.001)  # yield CPU; tasks self-throttle
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        bot.motors.stop()
        bot.leds.off_all()
        bot.ultrasonic.disable()
        bot.servos.home()

print("Done.")
