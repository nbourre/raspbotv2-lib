"""
Servo control module.

Controls pan/tilt servo channels via I2C register 0x02.

* Servo 1 (PAN):  0–180°
* Servo 2 (TILT): 0–110° (hardware limited)
"""

from __future__ import annotations

import logging

from raspbot.bus import I2CBus
from raspbot.types import Reg, ServoId, SERVO_TILT_MAX_ANGLE

logger = logging.getLogger(__name__)

_SERVO_MIN_ANGLE = 0
_SERVO_MAX_ANGLE = 180


class Servo:
    """Controls a single servo channel.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    servo_id:
        Which servo to control (:class:`~raspbot.types.ServoId`).
    """

    def __init__(self, bus: I2CBus, servo_id: ServoId | int) -> None:
        self._bus = bus
        self._id = int(servo_id)
        self._max_angle = (
            SERVO_TILT_MAX_ANGLE if self._id == ServoId.TILT else _SERVO_MAX_ANGLE
        )

    @property
    def max_angle(self) -> int:
        """Maximum allowed angle for this servo."""
        return self._max_angle

    def set_angle(self, angle: int) -> None:
        """Move the servo to *angle* degrees.

        The angle is clamped to the valid range for this servo channel.

        Parameters
        ----------
        angle:
            Target angle in degrees (0–180, or 0–110 for the tilt servo).
        """
        angle = max(_SERVO_MIN_ANGLE, min(self._max_angle, int(angle)))
        logger.debug("Servo %d -> %d°", self._id, angle)
        self._bus.write_block_data(Reg.SERVO, [self._id, angle])

    def home(self) -> None:
        """Move the servo to 90° (centre position)."""
        self.set_angle(90)


class ServoPair:
    """Convenience wrapper managing both pan and tilt servos together.

    Parameters
    ----------
    bus:
        Shared :class:`~raspbot.bus.I2CBus` instance.
    """

    def __init__(self, bus: I2CBus) -> None:
        self.pan = Servo(bus, ServoId.PAN)
        self.tilt = Servo(bus, ServoId.TILT)

    def home(self) -> None:
        """Move both servos to their home positions (pan 90°, tilt 25°)."""
        self.pan.set_angle(90)
        self.tilt.set_angle(25)
