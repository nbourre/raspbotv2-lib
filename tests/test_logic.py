"""Tests for pure-logic modules: types, exceptions, line_tracker parsing, and Task."""

from __future__ import annotations

from raspbot.exceptions import DeviceNotFoundError, I2CError, OLEDError, RaspbotError
from raspbot.sensors.line_tracker import LineState, _parse_line_byte
from raspbot.types import LedColor, MotorDirection, MotorId, ServoId
from raspbot.utils.task import Task

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
        assert MotorId.L1.value == 0
        assert MotorId.L2.value == 1
        assert MotorId.R1.value == 2
        assert MotorId.R2.value == 3

    def test_iteration(self) -> None:
        assert list(MotorId) == [MotorId.L1, MotorId.L2, MotorId.R1, MotorId.R2]


class TestMotorDirection:
    def test_values(self) -> None:
        assert MotorDirection.FORWARD.value == 0
        assert MotorDirection.REVERSE.value == 1


class TestServoId:
    def test_values(self) -> None:
        assert ServoId.PAN.value == 1
        assert ServoId.TILT.value == 2


class TestLedColor:
    def test_seven_colours(self) -> None:
        assert len(LedColor) == 7

    def test_red_is_zero(self) -> None:
        assert LedColor.RED.value == 0


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


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TestTask:
    def test_runs_immediately_on_first_call_by_default(self) -> None:
        calls: list[float] = []
        task = Task(lambda ct: calls.append(ct), rate=10.0)
        task(0.0)
        assert len(calls) == 1

    def test_does_not_run_before_rate_elapsed(self) -> None:
        calls: list[float] = []
        task = Task(lambda ct: calls.append(ct), rate=1.0)
        task(0.0)   # fires (first call)
        task(0.5)   # too soon
        task(0.9)   # too soon
        assert len(calls) == 1

    def test_runs_again_after_rate_elapsed(self) -> None:
        calls: list[float] = []
        task = Task(lambda ct: calls.append(ct), rate=1.0)
        task(0.0)   # fires
        task(1.0)   # exactly rate elapsed -- fires
        assert len(calls) == 2

    def test_run_immediately_false_skips_first_call(self) -> None:
        calls: list[float] = []
        task = Task(lambda ct: calls.append(ct), rate=1.0, run_immediately=False)
        task(0.0)   # should NOT fire -- waiting for first full period
        assert len(calls) == 0

    def test_run_immediately_false_fires_after_rate(self) -> None:
        calls: list[float] = []
        task = Task(lambda ct: calls.append(ct), rate=1.0, run_immediately=False)
        task(0.0)   # skipped
        task(1.01)  # fires
        assert len(calls) == 1

    def test_reset_causes_immediate_next_fire(self) -> None:
        calls: list[float] = []
        task = Task(lambda ct: calls.append(ct), rate=10.0)
        task(0.0)   # fires
        task(1.0)   # too soon
        task.reset()
        task(1.0)   # fires again after reset
        assert len(calls) == 2

    def test_rate_property_can_be_changed(self) -> None:
        calls: list[float] = []
        task = Task(lambda ct: calls.append(ct), rate=1.0)
        task(0.0)   # fires
        task.rate = 0.3
        task(0.3)   # now fires at new rate
        assert len(calls) == 2

    def test_every_decorator(self) -> None:
        calls: list[float] = []

        @Task.every(1.0)
        def my_task(ct: float) -> None:
            calls.append(ct)

        my_task(0.0)   # fires
        my_task(0.5)   # too soon
        my_task(1.0)   # fires
        assert len(calls) == 2

    def test_every_decorator_returns_task_instance(self) -> None:
        @Task.every(0.5)
        def my_task(ct: float) -> None:
            pass

        assert isinstance(my_task, Task)

    def test_repr_contains_fn_name_and_rate(self) -> None:
        def my_fn(ct: float) -> None:
            pass

        task = Task(my_fn, rate=2.5)
        assert "my_fn" in repr(task)
        assert "2.5" in repr(task)
