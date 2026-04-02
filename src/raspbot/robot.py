"""
High-level Robot facade.

:class:`Robot` is the single entry-point for controlling the Raspbot V2.  It
owns a shared :class:`~raspbot.bus.I2CBus` and exposes all hardware subsystems
as attributes, so callers don't need to wire bus instances together manually::

    from raspbot import Robot

    with Robot() as bot:
        bot.motors.forward(speed=150)
        time.sleep(1)
        bot.motors.stop()
        print(bot.ultrasonic.read_cm(), "cm")
"""

from __future__ import annotations

import contextlib
import logging

from raspbot.actuators.buzzer import Buzzer
from raspbot.actuators.led_bar import LedBar
from raspbot.actuators.motors import Motors
from raspbot.actuators.servo import ServoPair
from raspbot.bus import I2CBus
from raspbot.effects.light_effects import LightEffects
from raspbot.sensors.ir import IRReceiver
from raspbot.sensors.line_tracker import LineTracker
from raspbot.sensors.ultrasonic import UltrasonicSensor
from raspbot.types import RASPBOT_I2C_ADDRESS, RASPBOT_I2C_BUS

logger = logging.getLogger(__name__)


class Robot:
    """Facade for all Raspbot V2 hardware subsystems.

    Parameters
    ----------
    i2c_address:
        I2C address of the Raspbot microcontroller (default ``0x2B``).
    i2c_bus:
        Linux I2C bus number (default ``1``).

    Attributes
    ----------
    motors : Motors
        Four-wheel drive motor controller.
    servos : ServoPair
        Pan/tilt servo pair.
    buzzer : Buzzer
        Piezo buzzer.
    leds : LedBar
        14-LED WS2812 RGB light bar.
    ultrasonic : UltrasonicSensor
        HC-SR04-compatible distance sensor.
    line_tracker : LineTracker
        Four-channel IR line-tracking array.
    ir : IRReceiver
        IR remote-control receiver.
    light_effects : LightEffects
        Animated LED effect engine.
    """

    def __init__(
        self,
        i2c_address: int = RASPBOT_I2C_ADDRESS,
        i2c_bus: int = RASPBOT_I2C_BUS,
    ) -> None:
        self._bus = I2CBus(address=i2c_address, bus=i2c_bus)

        self.motors = Motors(self._bus)
        self.servos = ServoPair(self._bus)
        self.buzzer = Buzzer(self._bus)
        self.leds = LedBar(self._bus)
        self.ultrasonic = UltrasonicSensor(self._bus)
        self.line_tracker = LineTracker(self._bus)
        self.ir = IRReceiver(self._bus)
        self.light_effects = LightEffects(self.leds)

        logger.debug("Robot initialised (bus=%d, addr=0x%02X)", i2c_bus, i2c_address)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Safely stop all actuators and release the I2C bus."""
        with contextlib.suppress(Exception):
            self.motors.stop()
        with contextlib.suppress(Exception):
            self.leds.off_all()
        with contextlib.suppress(Exception):
            self.buzzer.off()
        self._bus.close()
        logger.debug("Robot closed")

    def __enter__(self) -> Robot:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Robot(bus={self._bus._bus_num}, addr=0x{self._bus._address:02X})"
