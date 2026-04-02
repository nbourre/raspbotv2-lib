"""
Shared types and enumerations used across the raspbot library.
"""

from __future__ import annotations

from enum import IntEnum


class MotorId(IntEnum):
    """Identifies one of the four drive motors."""

    L1 = 0  # Left front
    L2 = 1  # Left rear
    R1 = 2  # Right front
    R2 = 3  # Right rear


class MotorDirection(IntEnum):
    """Motor rotation direction."""

    FORWARD = 0
    REVERSE = 1


class ServoId(IntEnum):
    """Identifies a servo channel."""

    PAN = 1   # Horizontal / pan axis
    TILT = 2  # Vertical / tilt axis (hardware limited to 110°)


class LedColor(IntEnum):
    """Predefined colour codes for WS2812 LEDs (register-level values)."""

    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    PURPLE = 4
    CYAN = 5
    WHITE = 6


class LightEffect(str):
    """Named LED animation effects."""

    RIVER = "river"
    BREATHING = "breathing"
    GRADIENT = "gradient"
    RANDOM = "random_running"
    STARLIGHT = "starlight"


# Register map for the Raspbot V2 I2C microcontroller
class _Reg:
    MOTOR = 0x01
    SERVO = 0x02
    LED_ALL = 0x03
    LED_SINGLE = 0x04
    IR_SWITCH = 0x05
    BEEP = 0x06
    ULTRASONIC_SWITCH = 0x07
    LED_BRIGHTNESS_ALL = 0x08
    LED_BRIGHTNESS_SINGLE = 0x09
    LINE_TRACKER = 0x0A
    IR_KEYCODE = 0x0C
    ULTRASONIC_LOW = 0x1A
    ULTRASONIC_HIGH = 0x1B


# Make the register map available but signal it is internal
Reg = _Reg()

# Hardware constants
RASPBOT_I2C_ADDRESS: int = 0x2B
RASPBOT_I2C_BUS: int = 1
SERVO_TILT_MAX_ANGLE: int = 110  # hardware limitation for servo 2
NUM_LEDS: int = 14
