"""
01_motors.py - DC motor control

Demonstrates all Motors methods:
  - forward / backward / turn_left / turn_right / stop
  - set()  for explicit direction + speed per motor
  - drive() for signed speed (-255..+255) per motor

Run on Raspberry Pi with the Raspbot V2 powered on.
"""

import time

from raspbot import Robot
from raspbot.types import MotorDirection, MotorId

# The context manager guarantees motors are stopped and I2C is released
# even if the script is interrupted by Ctrl+C or an exception.
with Robot() as bot:
    # ------------------------------------------------------------------
    # High-level convenience helpers
    # ------------------------------------------------------------------

    print("Forward 1 s ...")
    bot.motors.forward(speed=150)
    time.sleep(1)

    print("Backward 1 s ...")
    bot.motors.backward(speed=150)
    time.sleep(1)

    print("Turn left 0.5 s ...")
    bot.motors.turn_left(speed=150)
    time.sleep(0.5)

    print("Turn right 0.5 s ...")
    bot.motors.turn_right(speed=150)
    time.sleep(0.5)

    bot.motors.stop()
    time.sleep(0.3)

    # ------------------------------------------------------------------
    # Low-level: set() -- explicit motor id, direction, and speed
    # ------------------------------------------------------------------

    print("Low-level set(): L1 forward at 100 ...")
    bot.motors.set(MotorId.L1, MotorDirection.FORWARD, 100)
    time.sleep(0.5)
    bot.motors.stop()
    time.sleep(0.3)

    # ------------------------------------------------------------------
    # Low-level: drive() -- signed speed, negative = reverse
    # ------------------------------------------------------------------

    print("drive() all motors with signed speed ...")
    for motor in MotorId:
        bot.motors.drive(motor, 120)  # forward
    time.sleep(0.5)

    for motor in MotorId:
        bot.motors.drive(motor, -120)  # reverse
    time.sleep(0.5)

    bot.motors.stop()

print("Done.")
