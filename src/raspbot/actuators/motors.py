"""
Motor control module.

Controls the four DC drive motors of the Raspbot V2 via I2C register 0x01.

Motor layout (viewed from above)::

    L1 (front-left)  R1 (front-right)
    L2 (rear-left)   R2 (rear-right)

Mecanum wheel roller orientation (standard X-pattern)::

    L1: rollers at +45 deg  (/)    R1: rollers at -45 deg  (\\)
    L2: rollers at -45 deg  (\\)   R2: rollers at +45 deg  (/)

This produces the following motion for each motor combination:

    Movement           L1     L2     R1     R2
    forward            FWD    FWD    FWD    FWD
    backward           REV    REV    REV    REV
    rotate_left        REV    REV    FWD    FWD
    rotate_right       FWD    FWD    REV    REV
    strafe_right       FWD    REV    REV    FWD
    strafe_left        REV    FWD    FWD    REV
    diagonal_fwd_right FWD    stop   stop   FWD
    diagonal_fwd_left  stop   FWD    FWD    stop
    diagonal_bwd_right stop   REV    REV    stop
    diagonal_bwd_left  REV    stop   stop   REV
"""

from __future__ import annotations

import logging

from raspbot.bus import I2CBus
from raspbot.types import MotorDirection, MotorId, Reg

logger = logging.getLogger(__name__)

_SPEED_MAX = 255
_SPEED_MIN = 0


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


class Motors:
    """Controls all four drive motors.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self._bus = bus

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set(
        self,
        motor_id: MotorId | int,
        direction: MotorDirection | int,
        speed: int,
    ) -> None:
        """Set *direction* and *speed* for a single motor.

        Parameters
        ----------
        motor_id:
            Which motor to control (0-3 or :class:`~raspbot.types.MotorId`).
        direction:
            :attr:`~raspbot.types.MotorDirection.FORWARD` (0) or
            :attr:`~raspbot.types.MotorDirection.REVERSE` (1).
        speed:
            PWM duty-cycle 0-255 (0 = stopped, 255 = full speed).
        """
        motor_id = int(motor_id)
        direction = int(direction) if int(direction) in (0, 1) else 0
        speed = _clamp(int(speed), _SPEED_MIN, _SPEED_MAX)
        logger.debug("Motor %d dir=%d speed=%d", motor_id, direction, speed)
        self._bus.write_block_data(Reg.MOTOR, [motor_id, direction, speed])

    def drive(self, motor_id: MotorId | int, speed: int) -> None:
        """Drive a motor with a *signed* speed value.

        Parameters
        ----------
        motor_id:
            Which motor to control.
        speed:
            Signed speed −255 … +255.  Negative values drive in reverse.
        """
        speed = _clamp(int(speed), -_SPEED_MAX, _SPEED_MAX)
        direction = MotorDirection.REVERSE if speed < 0 else MotorDirection.FORWARD
        self.set(motor_id, direction, abs(speed))

    def forward(self, speed: int = 150) -> None:
        """Drive all four motors forward at *speed*."""
        for mid in MotorId:
            self.set(mid, MotorDirection.FORWARD, speed)

    def backward(self, speed: int = 150) -> None:
        """Drive all four motors backward at *speed*."""
        for mid in MotorId:
            self.set(mid, MotorDirection.REVERSE, speed)

    def turn_left(self, speed: int = 150) -> None:
        """Spin left: right motors forward, left motors reverse."""
        self.set(MotorId.L1, MotorDirection.REVERSE, speed)
        self.set(MotorId.L2, MotorDirection.REVERSE, speed)
        self.set(MotorId.R1, MotorDirection.FORWARD, speed)
        self.set(MotorId.R2, MotorDirection.FORWARD, speed)

    def turn_right(self, speed: int = 150) -> None:
        """Spin right: left motors forward, right motors reverse."""
        self.set(MotorId.L1, MotorDirection.FORWARD, speed)
        self.set(MotorId.L2, MotorDirection.FORWARD, speed)
        self.set(MotorId.R1, MotorDirection.REVERSE, speed)
        self.set(MotorId.R2, MotorDirection.REVERSE, speed)

    # ------------------------------------------------------------------
    # Mecanum-specific moves (require X-pattern roller orientation)
    # ------------------------------------------------------------------

    def strafe_right(self, speed: int = 150) -> None:
        """Slide directly right without rotating (mecanum only).

        Motor pattern::

            L1: forward    R1: reverse
            L2: reverse    R2: forward

        Parameters
        ----------
        speed:
            PWM duty-cycle 0-255.
        """
        speed = _clamp(int(speed), _SPEED_MIN, _SPEED_MAX)
        self.set(MotorId.L1, MotorDirection.FORWARD, speed)
        self.set(MotorId.L2, MotorDirection.REVERSE, speed)
        self.set(MotorId.R1, MotorDirection.REVERSE, speed)
        self.set(MotorId.R2, MotorDirection.FORWARD, speed)

    def strafe_left(self, speed: int = 150) -> None:
        """Slide directly left without rotating (mecanum only).

        Motor pattern::

            L1: reverse    R1: forward
            L2: forward    R2: reverse

        Parameters
        ----------
        speed:
            PWM duty-cycle 0-255.
        """
        speed = _clamp(int(speed), _SPEED_MIN, _SPEED_MAX)
        self.set(MotorId.L1, MotorDirection.REVERSE, speed)
        self.set(MotorId.L2, MotorDirection.FORWARD, speed)
        self.set(MotorId.R1, MotorDirection.FORWARD, speed)
        self.set(MotorId.R2, MotorDirection.REVERSE, speed)

    def diagonal_forward_right(self, speed: int = 150) -> None:
        """Drive diagonally forward-right at 45 degrees (mecanum only).

        Only L1 (front-left) and R2 (rear-right) are driven; the other
        two motors are stopped.

        Parameters
        ----------
        speed:
            PWM duty-cycle 0-255 for the active motors.
        """
        speed = _clamp(int(speed), _SPEED_MIN, _SPEED_MAX)
        self.set(MotorId.L1, MotorDirection.FORWARD, speed)
        self.set(MotorId.L2, MotorDirection.FORWARD, 0)
        self.set(MotorId.R1, MotorDirection.FORWARD, 0)
        self.set(MotorId.R2, MotorDirection.FORWARD, speed)

    def diagonal_forward_left(self, speed: int = 150) -> None:
        """Drive diagonally forward-left at 45 degrees (mecanum only).

        Only L2 (rear-left) and R1 (front-right) are driven.

        Parameters
        ----------
        speed:
            PWM duty-cycle 0-255 for the active motors.
        """
        speed = _clamp(int(speed), _SPEED_MIN, _SPEED_MAX)
        self.set(MotorId.L1, MotorDirection.FORWARD, 0)
        self.set(MotorId.L2, MotorDirection.FORWARD, speed)
        self.set(MotorId.R1, MotorDirection.FORWARD, speed)
        self.set(MotorId.R2, MotorDirection.FORWARD, 0)

    def diagonal_backward_right(self, speed: int = 150) -> None:
        """Drive diagonally backward-right at 45 degrees (mecanum only).

        Only L2 (rear-left) and R1 (front-right) are driven in reverse.

        Parameters
        ----------
        speed:
            PWM duty-cycle 0-255 for the active motors.
        """
        speed = _clamp(int(speed), _SPEED_MIN, _SPEED_MAX)
        self.set(MotorId.L1, MotorDirection.FORWARD, 0)
        self.set(MotorId.L2, MotorDirection.REVERSE, speed)
        self.set(MotorId.R1, MotorDirection.REVERSE, speed)
        self.set(MotorId.R2, MotorDirection.FORWARD, 0)

    def diagonal_backward_left(self, speed: int = 150) -> None:
        """Drive diagonally backward-left at 45 degrees (mecanum only).

        Only L1 (front-left) and R2 (rear-right) are driven in reverse.

        Parameters
        ----------
        speed:
            PWM duty-cycle 0-255 for the active motors.
        """
        speed = _clamp(int(speed), _SPEED_MIN, _SPEED_MAX)
        self.set(MotorId.L1, MotorDirection.REVERSE, speed)
        self.set(MotorId.L2, MotorDirection.FORWARD, 0)
        self.set(MotorId.R1, MotorDirection.FORWARD, 0)
        self.set(MotorId.R2, MotorDirection.REVERSE, speed)

    def stop(self) -> None:
        """Stop all motors immediately."""
        for mid in MotorId:
            self.set(mid, MotorDirection.FORWARD, 0)
