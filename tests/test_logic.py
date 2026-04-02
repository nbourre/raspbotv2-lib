"""Tests for pure-logic modules: types, exceptions, and line_tracker parsing."""

from __future__ import annotations

import pytest

from raspbot.exceptions import DeviceNotFoundError, I2CError, OLEDError, RaspbotError
from raspbot.sensors.line_tracker import LineState, _parse_line_byte
from raspbot.types import LedColor, MotorDirection, MotorId, ServoId


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class TestExceptions:
    def test_i2c_error_is_raspbot_error(self) -> None:
        err = I2CError("write")
        assert isinstance(err, RaspbotError)

    def test_device_not_found_is_raspbot_error(self) -> None:
        err = DeviceNotFoundError(0x2B, 1)
        assert isinstance(err, RaspbotError)
        assert err.address == 0x2B
        assert err.bus == 1

    def test_i2c_error_message_includes_operation(self) -> None:
        err = I2CError("read_block")
        assert "read_block" in str(err)

    def test_i2c_error_with_cause(self) -> None:
        cause = OSError("no device")
        err = I2CError("write_byte", cause)
        assert err.cause is cause
        assert "write_byte" in str(err)

    def test_oled_error_is_raspbot_error(self) -> None:
        assert isinstance(OLEDError("oops"), RaspbotError)


# ---------------------------------------------------------------------------
# Type enumerations
# ---------------------------------------------------------------------------

class TestMotorId:
    def test_values(self) -> None:
        assert MotorId.L1 == 0
        assert MotorId.L2 == 1
        assert MotorId.R1 == 2
        assert MotorId.R2 == 3

    def test_iteration(self) -> None:
        assert list(MotorId) == [MotorId.L1, MotorId.L2, MotorId.R1, MotorId.R2]


class TestMotorDirection:
    def test_values(self) -> None:
        assert MotorDirection.FORWARD == 0
        assert MotorDirection.REVERSE == 1


class TestServoId:
    def test_values(self) -> None:
        assert ServoId.PAN == 1
        assert ServoId.TILT == 2


class TestLedColor:
    def test_seven_colours(self) -> None:
        assert len(LedColor) == 7

    def test_red_is_zero(self) -> None:
        assert LedColor.RED == 0


# ---------------------------------------------------------------------------
# LineState / _parse_line_byte
# ---------------------------------------------------------------------------

class TestParseLine:
    def test_all_off(self) -> None:
        s = _parse_line_byte(0b0000)
        assert s == LineState(x1=False, x2=False, x3=False, x4=False, raw=0)
        assert not s.on_line

    def test_all_on(self) -> None:
        s = _parse_line_byte(0b1111)
        assert s.x1 and s.x2 and s.x3 and s.x4
        assert s.on_line

    def test_x1_only(self) -> None:
        s = _parse_line_byte(0b1000)
        assert s.x1
        assert not s.x2
        assert not s.x3
        assert not s.x4

    def test_x4_only(self) -> None:
        s = _parse_line_byte(0b0001)
        assert s.x4
        assert not s.x1

    def test_centered(self) -> None:
        s = _parse_line_byte(0b0110)
        assert s.centered

    def test_not_centered_when_only_x1(self) -> None:
        s = _parse_line_byte(0b1000)
        assert not s.centered

    def test_str_representation(self) -> None:
        s = _parse_line_byte(0b1010)
        assert str(s) == "LineState(1010)"

    def test_raw_preserved(self) -> None:
        s = _parse_line_byte(0b0101)
        assert s.raw == 0b0101
