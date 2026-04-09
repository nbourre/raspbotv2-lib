"""
raspbot - Python library for controlling the Yahboom Raspbot V2 robot car.

Quick start::

    from raspbot import Robot

    with Robot() as bot:
        bot.motors.forward(speed=150)
        import time; time.sleep(1)
        bot.motors.stop()
"""

from __future__ import annotations

try:
    from raspbot.camera.opencv_camera import Camera
    _CAMERA_AVAILABLE = True
except ImportError:
    _CAMERA_AVAILABLE = False  # type: ignore[assignment]

from raspbot.exceptions import (
    DeviceNotFoundError,
    HardwareNotReadyError,
    I2CError,
    OLEDError,
    RaspbotError,
)
from raspbot.robot import Robot
from raspbot.sensors.button import Button
from raspbot.types import (
    LedColor,
    LightEffect,
    MotorDirection,
    MotorId,
    ServoId,
)
from raspbot.utils.task import Task

__all__ = [
    "Robot",
    # Utilities
    "Task",
    # Sensors
    "Button",
    # Camera
    "Camera",
    # Exceptions
    "RaspbotError",
    "I2CError",
    "DeviceNotFoundError",
    "OLEDError",
    "HardwareNotReadyError",
    # Types / enums
    "MotorId",
    "MotorDirection",
    "ServoId",
    "LedColor",
    "LightEffect",
]

__version__ = "0.1.2"
