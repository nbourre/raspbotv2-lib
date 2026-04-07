"""
14_mecanum.py - Mecanum wheel movement demo

Demonstrates all movement modes available with the Yahboom Raspbot V2
mecanum wheel chassis. Mecanum wheels have rollers mounted at 45 degrees,
which allows lateral (sideways) and diagonal movement in addition to
normal forward/backward and in-place rotation.

Wheel roller orientation (standard X-pattern, viewed from above):

    FL (/): rollers at +45 deg    FR (\\): rollers at -45 deg
    RL (\\): rollers at -45 deg   RR (/): rollers at +45 deg

Movement matrix (F = forward, R = reverse, 0 = stopped):

    Movement           FL   RL   FR   RR
    forward             F    F    F    F
    backward            R    R    R    R
    rotate left         R    R    F    F
    rotate right        F    F    R    R
    strafe right        F    R    R    F
    strafe left         R    F    F    R
    diagonal fwd-right  F    0    0    F
    diagonal fwd-left   0    F    F    0
    diagonal bwd-right  R    0    0    R
    diagonal bwd-left   0    R    R    0

Run on Raspberry Pi with the Raspbot V2 powered on.

Usage:
    python 14_mecanum.py
"""

from __future__ import annotations

import time

from raspbot import Robot

SPEED = 150       # 0-255 -- reduce if the robot moves too fast
DURATION = 1.0    # seconds per movement

moves = [
    ("Forward",               lambda bot: bot.motors.forward(SPEED)),
    ("Backward",              lambda bot: bot.motors.backward(SPEED)),
    ("Rotate left",           lambda bot: bot.motors.turn_left(SPEED)),
    ("Rotate right",          lambda bot: bot.motors.turn_right(SPEED)),
    ("Strafe right",          lambda bot: bot.motors.strafe_right(SPEED)),
    ("Strafe left",           lambda bot: bot.motors.strafe_left(SPEED)),
    ("Diagonal fwd-right",    lambda bot: bot.motors.diagonal_forward_right(SPEED)),
    ("Diagonal fwd-left",     lambda bot: bot.motors.diagonal_forward_left(SPEED)),
    ("Diagonal bwd-right",    lambda bot: bot.motors.diagonal_backward_right(SPEED)),
    ("Diagonal bwd-left",     lambda bot: bot.motors.diagonal_backward_left(SPEED)),
]

with Robot() as bot:
    print("Mecanum wheel demo -- each move runs for", DURATION, "s")
    print("Place the robot in an open space before starting.\n")

    for name, move_fn in moves:
        print(f"  {name}...")
        move_fn(bot)
        time.sleep(DURATION)
        bot.motors.stop()
        time.sleep(0.3)   # brief pause between moves

    print("\nDemo complete.")
