"""
Unit tests for hardware modules using a mock I2CBus.

These tests verify that each module sends the correct I2C register/data
sequences without requiring real hardware.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from raspbot.actuators.buzzer import Buzzer
from raspbot.actuators.led_bar import LedBar
from raspbot.actuators.motors import Motors
from raspbot.actuators.servo import Servo, ServoPair
from raspbot.camera.opencv_camera import Camera
from raspbot.display.oled import OLED_HEIGHT, OLED_WIDTH, OLEDDisplay
from raspbot.effects.light_effects import LightEffects
from raspbot.exceptions import OLEDError
from raspbot.sensors.button import Button
from raspbot.sensors.ir import IRReceiver
from raspbot.sensors.line_tracker import LineTracker
from raspbot.sensors.ultrasonic import UltrasonicSensor
from raspbot.types import LedColor, MotorDirection, MotorId, Reg, ServoId

# ---------------------------------------------------------------------------
# Motors
# ---------------------------------------------------------------------------


class TestMotors:
    def test_set_forward(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.set(MotorId.L1, MotorDirection.FORWARD, 150)
        mock_bus.write_block_data.assert_called_once_with(Reg.MOTOR, [0, 0, 150])

    def test_set_clamps_speed_above_255(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.set(MotorId.R2, MotorDirection.FORWARD, 300)
        mock_bus.write_block_data.assert_called_once_with(Reg.MOTOR, [3, 0, 255])

    def test_set_clamps_speed_below_0(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.set(MotorId.L2, MotorDirection.FORWARD, -10)
        mock_bus.write_block_data.assert_called_once_with(Reg.MOTOR, [1, 0, 0])

    def test_drive_negative_is_reverse(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.drive(MotorId.R1, -100)
        mock_bus.write_block_data.assert_called_once_with(Reg.MOTOR, [2, 1, 100])

    def test_stop_sends_zero_speed_for_all_motors(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.stop()
        assert mock_bus.write_block_data.call_count == 4

    def test_forward_drives_all_four(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.forward(100)
        assert mock_bus.write_block_data.call_count == 4
        for c in mock_bus.write_block_data.call_args_list:
            _, data = c[0]
            assert data[1] == MotorDirection.FORWARD
            assert data[2] == 100

    # Mecanum moves

    def test_strafe_right_motor_pattern(self, mock_bus: MagicMock) -> None:
        # L1:FWD  L2:REV  R1:REV  R2:FWD
        m = Motors(mock_bus)
        m.strafe_right(120)
        calls = mock_bus.write_block_data.call_args_list
        assert call(Reg.MOTOR, [MotorId.L1, MotorDirection.FORWARD, 120]) in calls
        assert call(Reg.MOTOR, [MotorId.L2, MotorDirection.REVERSE, 120]) in calls
        assert call(Reg.MOTOR, [MotorId.R1, MotorDirection.REVERSE, 120]) in calls
        assert call(Reg.MOTOR, [MotorId.R2, MotorDirection.FORWARD, 120]) in calls

    def test_strafe_left_motor_pattern(self, mock_bus: MagicMock) -> None:
        # L1:REV  L2:FWD  R1:FWD  R2:REV
        m = Motors(mock_bus)
        m.strafe_left(120)
        calls = mock_bus.write_block_data.call_args_list
        assert call(Reg.MOTOR, [MotorId.L1, MotorDirection.REVERSE, 120]) in calls
        assert call(Reg.MOTOR, [MotorId.L2, MotorDirection.FORWARD, 120]) in calls
        assert call(Reg.MOTOR, [MotorId.R1, MotorDirection.FORWARD, 120]) in calls
        assert call(Reg.MOTOR, [MotorId.R2, MotorDirection.REVERSE, 120]) in calls

    def test_diagonal_forward_right_pattern(self, mock_bus: MagicMock) -> None:
        # L1:FWD  L2:stop  R1:stop  R2:FWD
        m = Motors(mock_bus)
        m.diagonal_forward_right(130)
        calls = mock_bus.write_block_data.call_args_list
        assert call(Reg.MOTOR, [MotorId.L1, MotorDirection.FORWARD, 130]) in calls
        assert call(Reg.MOTOR, [MotorId.L2, MotorDirection.FORWARD, 0]) in calls
        assert call(Reg.MOTOR, [MotorId.R1, MotorDirection.FORWARD, 0]) in calls
        assert call(Reg.MOTOR, [MotorId.R2, MotorDirection.FORWARD, 130]) in calls

    def test_diagonal_forward_left_pattern(self, mock_bus: MagicMock) -> None:
        # L1:stop  L2:FWD  R1:FWD  R2:stop
        m = Motors(mock_bus)
        m.diagonal_forward_left(130)
        calls = mock_bus.write_block_data.call_args_list
        assert call(Reg.MOTOR, [MotorId.L1, MotorDirection.FORWARD, 0]) in calls
        assert call(Reg.MOTOR, [MotorId.L2, MotorDirection.FORWARD, 130]) in calls
        assert call(Reg.MOTOR, [MotorId.R1, MotorDirection.FORWARD, 130]) in calls
        assert call(Reg.MOTOR, [MotorId.R2, MotorDirection.FORWARD, 0]) in calls

    def test_diagonal_backward_right_pattern(self, mock_bus: MagicMock) -> None:
        # L1:REV  L2:stop  R1:stop  R2:REV
        m = Motors(mock_bus)
        m.diagonal_backward_right(130)
        calls = mock_bus.write_block_data.call_args_list
        assert call(Reg.MOTOR, [MotorId.L1, MotorDirection.REVERSE, 130]) in calls
        assert call(Reg.MOTOR, [MotorId.L2, MotorDirection.FORWARD, 0]) in calls
        assert call(Reg.MOTOR, [MotorId.R1, MotorDirection.FORWARD, 0]) in calls
        assert call(Reg.MOTOR, [MotorId.R2, MotorDirection.REVERSE, 130]) in calls

    def test_diagonal_backward_left_pattern(self, mock_bus: MagicMock) -> None:
        # L1:stop  L2:REV  R1:REV  R2:stop
        m = Motors(mock_bus)
        m.diagonal_backward_left(130)
        calls = mock_bus.write_block_data.call_args_list
        assert call(Reg.MOTOR, [MotorId.L1, MotorDirection.FORWARD, 0]) in calls
        assert call(Reg.MOTOR, [MotorId.L2, MotorDirection.REVERSE, 130]) in calls
        assert call(Reg.MOTOR, [MotorId.R1, MotorDirection.REVERSE, 130]) in calls
        assert call(Reg.MOTOR, [MotorId.R2, MotorDirection.FORWARD, 0]) in calls

    def test_strafe_clamps_speed_above_255(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.strafe_right(300)
        for c in mock_bus.write_block_data.call_args_list:
            _, data = c[0]
            assert data[2] <= 255

    def test_strafe_sends_four_commands(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.strafe_left(100)
        assert mock_bus.write_block_data.call_count == 4

    def test_diagonal_sends_four_commands(self, mock_bus: MagicMock) -> None:
        m = Motors(mock_bus)
        m.diagonal_forward_right(100)
        assert mock_bus.write_block_data.call_count == 4


# ---------------------------------------------------------------------------
# Servo
# ---------------------------------------------------------------------------


class TestServo:
    def test_set_angle(self, mock_bus: MagicMock) -> None:
        s = Servo(mock_bus, ServoId.PAN)
        s.set_angle(90)
        mock_bus.write_block_data.assert_called_once_with(Reg.SERVO, [1, 90])

    def test_tilt_clamped_to_110(self, mock_bus: MagicMock) -> None:
        s = Servo(mock_bus, ServoId.TILT)
        s.set_angle(180)
        mock_bus.write_block_data.assert_called_once_with(Reg.SERVO, [2, 110])

    def test_angle_clamped_to_zero(self, mock_bus: MagicMock) -> None:
        s = Servo(mock_bus, ServoId.PAN)
        s.set_angle(-5)
        mock_bus.write_block_data.assert_called_once_with(Reg.SERVO, [1, 0])

    def test_home_moves_to_90(self, mock_bus: MagicMock) -> None:
        s = Servo(mock_bus, ServoId.PAN)
        s.home()
        mock_bus.write_block_data.assert_called_once_with(Reg.SERVO, [1, 90])

    def test_servo_pair_home(self, mock_bus: MagicMock) -> None:
        sp = ServoPair(mock_bus)
        sp.home()
        calls = mock_bus.write_block_data.call_args_list
        assert call(Reg.SERVO, [1, 90]) in calls
        assert call(Reg.SERVO, [2, 25]) in calls


# ---------------------------------------------------------------------------
# Buzzer
# ---------------------------------------------------------------------------


class TestBuzzer:
    def test_on(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.on()
        mock_bus.write_block_data.assert_called_once_with(Reg.BEEP, [1])

    def test_off(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.off()
        mock_bus.write_block_data.assert_called_once_with(Reg.BEEP, [0])

    def test_idle_is_not_active(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        assert not b.is_active

    def test_beep_turns_on_immediately(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.beep(0.2)
        mock_bus.write_block_data.assert_called_with(Reg.BEEP, [1])
        assert b.is_active

    def test_beep_turns_off_after_duration(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.beep(0.2)
        # First update() stamps the deadline
        b.update(0.0)
        # Before deadline -- still on
        b.update(0.1)
        assert b._buzzer_on
        # After deadline -- should turn off
        b.update(0.3)
        calls = mock_bus.write_block_data.call_args_list
        # on() during beep(), off() after deadline
        assert calls[-1] == call(Reg.BEEP, [0])
        assert not b.is_active

    def test_beep_inactive_after_done(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.beep(0.1)
        b.update(0.0)
        b.update(1.0)  # well past deadline
        assert not b.is_active

    def test_pattern_emits_correct_on_off_count(self, mock_bus: MagicMock) -> None:
        # 3-beep pattern with on_time=0.1, off_time=0.1
        b = Buzzer(mock_bus)
        b.pattern(0.1, 0.1, 3)
        # Simulate the full sequence by advancing time through all phases
        # t=0: beep() called, buzzer on (call 1)
        # update at t=0: stamps deadline at 0.1
        b.update(0.0)
        # t=0.15: first ON expires -> off (call 2), schedule OFF gap end at 0.25
        b.update(0.15)
        # t=0.30: OFF gap expires -> on (call 3), schedule ON end at 0.40
        b.update(0.30)
        # t=0.45: second ON expires -> off (call 4), schedule OFF gap end at 0.55
        b.update(0.45)
        # t=0.60: OFF gap expires -> on (call 5), schedule ON end at 0.70
        b.update(0.60)
        # t=0.75: third ON expires -> off (call 6), done
        b.update(0.75)

        on_calls  = [c for c in mock_bus.write_block_data.call_args_list if c == call(Reg.BEEP, [1])]
        off_calls = [c for c in mock_bus.write_block_data.call_args_list if c == call(Reg.BEEP, [0])]
        assert len(on_calls)  == 3
        assert len(off_calls) == 3
        assert not b.is_active

    def test_pattern_zero_count_does_nothing(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.pattern(0.1, 0.1, 0)
        assert not b.is_active
        mock_bus.write_block_data.assert_not_called()

    def test_beep_zero_duration_does_nothing(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.beep(0)
        assert not b.is_active
        mock_bus.write_block_data.assert_not_called()

    def test_update_when_idle_does_nothing(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        b.update(1.0)
        mock_bus.write_block_data.assert_not_called()


# ---------------------------------------------------------------------------
# LightEffects
# ---------------------------------------------------------------------------


class TestLightEffects:
    """Tests for the non-blocking LightEffects state machine."""

    def _make(self, mock_bus: MagicMock) -> tuple[LightEffects, LedBar]:
        bar = LedBar(mock_bus)
        fx = LightEffects(bar)
        return fx, bar

    def test_idle_is_not_active(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        assert not fx.is_active

    def test_stop_before_start_does_not_raise(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.stop()  # must not raise

    def test_update_when_idle_does_nothing(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.update(0.0)
        mock_bus.write_block_data.assert_not_called()

    def test_start_river_marks_active(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_river(speed=0.05)
        assert fx.is_active

    def test_river_update_calls_set_one(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_river(speed=0.05)
        fx.update(0.0)   # first frame
        # set_one should have been called (3 LEDs in the group)
        assert mock_bus.write_block_data.call_count >= 1

    def test_river_update_rate_gates(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_river(speed=0.1)
        fx.update(0.0)  # frame 1
        count_after_first = mock_bus.write_block_data.call_count
        fx.update(0.05)  # too soon -- should be gated out
        assert mock_bus.write_block_data.call_count == count_after_first

    def test_stop_turns_off_leds(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_river()
        fx.stop()
        assert not fx.is_active
        # off_all() must have been called
        mock_bus.write_block_data.assert_called()

    def test_start_breathing_marks_active(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_breathing(LedColor.RED, speed=0.01)
        assert fx.is_active

    def test_breathing_update_calls_set_brightness_all(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_breathing(LedColor.BLUE, speed=0.01)
        fx.update(0.0)
        mock_bus.write_block_data.assert_called()

    def test_start_random_running_marks_active(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_random_running(speed=0.05)
        assert fx.is_active

    def test_random_running_update_sets_all_leds(self, mock_bus: MagicMock) -> None:
        from raspbot.types import NUM_LEDS
        fx, _ = self._make(mock_bus)
        fx.start_random_running(speed=0.05)
        fx.update(0.0)
        # set_one is called once per LED
        assert mock_bus.write_block_data.call_count == NUM_LEDS

    def test_start_starlight_marks_active(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_starlight(speed=0.1)
        assert fx.is_active

    def test_starlight_update_writes_leds(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_starlight(speed=0.1)
        fx.update(0.0)
        mock_bus.write_block_data.assert_called()

    def test_start_gradient_marks_active(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_gradient(speed=0.02)
        assert fx.is_active

    def test_gradient_update_writes_leds(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_gradient(speed=0.02)
        fx.update(0.0)
        mock_bus.write_block_data.assert_called()

    def test_off_alias_for_stop(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_river()
        fx.off()
        assert not fx.is_active

    def test_restart_replaces_current_effect(self, mock_bus: MagicMock) -> None:
        fx, _ = self._make(mock_bus)
        fx.start_river()
        fx.start_breathing()  # should replace without errors
        assert fx.is_active


# ---------------------------------------------------------------------------
# LedBar
# ---------------------------------------------------------------------------


class TestLedBar:
    def test_set_all_on(self, mock_bus: MagicMock) -> None:
        lb = LedBar(mock_bus)
        lb.set_all(LedColor.BLUE)
        mock_bus.write_block_data.assert_called_once_with(Reg.LED_ALL, [1, 2])

    def test_set_all_off(self, mock_bus: MagicMock) -> None:
        lb = LedBar(mock_bus)
        lb.set_all(LedColor.GREEN, on=False)
        mock_bus.write_block_data.assert_called_once_with(Reg.LED_ALL, [0, 1])

    def test_off_all(self, mock_bus: MagicMock) -> None:
        lb = LedBar(mock_bus)
        lb.off_all()
        mock_bus.write_block_data.assert_called_once_with(Reg.LED_ALL, [0, LedColor.RED])

    def test_set_one(self, mock_bus: MagicMock) -> None:
        lb = LedBar(mock_bus)
        lb.set_one(5, LedColor.YELLOW)
        mock_bus.write_block_data.assert_called_once_with(Reg.LED_SINGLE, [5, 1, 3])

    def test_brightness_all_clamped(self, mock_bus: MagicMock) -> None:
        lb = LedBar(mock_bus)
        lb.set_brightness_all(300, -10, 128)
        mock_bus.write_block_data.assert_called_once_with(Reg.LED_BRIGHTNESS_ALL, [255, 0, 128])

    def test_brightness_one(self, mock_bus: MagicMock) -> None:
        lb = LedBar(mock_bus)
        lb.set_brightness_one(7, 100, 200, 50)
        mock_bus.write_block_data.assert_called_once_with(
            Reg.LED_BRIGHTNESS_SINGLE, [7, 100, 200, 50]
        )

    def test_count(self, mock_bus: MagicMock) -> None:
        lb = LedBar(mock_bus)
        assert lb.count == 14


# ---------------------------------------------------------------------------
# UltrasonicSensor
# ---------------------------------------------------------------------------


class TestUltrasonic:
    def test_read_mm_combines_high_and_low(self, mock_bus: MagicMock) -> None:
        sensor = UltrasonicSensor(mock_bus)
        sensor._enabled = True  # skip warmup
        mock_bus.read_block_data.side_effect = lambda reg, _: (
            [0x01] if reg == Reg.ULTRASONIC_HIGH else [0x90]
        )
        distance = sensor.read_mm()
        # 0x01 << 8 | 0x90 = 400
        assert distance == 0x0190

    def test_read_cm(self, mock_bus: MagicMock) -> None:
        sensor = UltrasonicSensor(mock_bus)
        sensor._enabled = True
        mock_bus.read_block_data.side_effect = lambda reg, _: (
            [0x00] if reg == Reg.ULTRASONIC_HIGH else [0x64]  # 100 mm
        )
        assert sensor.read_cm() == pytest.approx(10.0)

    def test_enable_sends_correct_register(self, mock_bus: MagicMock) -> None:
        sensor = UltrasonicSensor(mock_bus)
        with patch("raspbot.sensors.ultrasonic.time.sleep"):
            sensor.enable()
        mock_bus.write_block_data.assert_called_once_with(Reg.ULTRASONIC_SWITCH, [1])

    def test_disable_sends_correct_register(self, mock_bus: MagicMock) -> None:
        sensor = UltrasonicSensor(mock_bus)
        sensor.disable()
        mock_bus.write_block_data.assert_called_once_with(Reg.ULTRASONIC_SWITCH, [0])


# ---------------------------------------------------------------------------
# LineTracker
# ---------------------------------------------------------------------------


class TestLineTracker:
    def test_read_parses_byte(self, mock_bus: MagicMock) -> None:
        tracker = LineTracker(mock_bus)
        mock_bus.read_block_data.return_value = [0b1010]
        state = tracker.read()
        assert state.x1 is True
        assert state.x2 is False
        assert state.x3 is True
        assert state.x4 is False

    def test_read_calls_correct_register(self, mock_bus: MagicMock) -> None:
        tracker = LineTracker(mock_bus)
        mock_bus.read_block_data.return_value = [0]
        tracker.read()
        mock_bus.read_block_data.assert_called_once_with(Reg.LINE_TRACKER, 1)


# ---------------------------------------------------------------------------
# IRReceiver
# ---------------------------------------------------------------------------


class TestIRReceiver:
    def test_enable(self, mock_bus: MagicMock) -> None:
        ir = IRReceiver(mock_bus)
        ir.enable()
        mock_bus.write_block_data.assert_called_once_with(Reg.IR_SWITCH, [1])

    def test_disable(self, mock_bus: MagicMock) -> None:
        ir = IRReceiver(mock_bus)
        ir.disable()
        mock_bus.write_block_data.assert_called_once_with(Reg.IR_SWITCH, [0])

    def test_read_keycode_returns_value(self, mock_bus: MagicMock) -> None:
        ir = IRReceiver(mock_bus)
        ir._enabled = True
        mock_bus.read_block_data.return_value = [0x45]
        assert ir.read_keycode() == 0x45

    def test_read_keycode_returns_none_when_zero(self, mock_bus: MagicMock) -> None:
        ir = IRReceiver(mock_bus)
        ir._enabled = True
        mock_bus.read_block_data.return_value = [0]
        assert ir.read_keycode() is None


# ---------------------------------------------------------------------------
# OLEDDisplay
# ---------------------------------------------------------------------------


def _make_oled_mocks() -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    """Return (mock_device, mock_image, mock_draw, mock_font)."""
    mock_device = MagicMock()
    mock_image = MagicMock()
    mock_draw = MagicMock()
    mock_font = MagicMock()
    return mock_device, mock_image, mock_draw, mock_font


def _patch_deps(
    mock_device: MagicMock,
    mock_image: MagicMock,
    mock_draw: MagicMock,
    mock_font: MagicMock,
) -> Any:
    """Return a patcher for _import_oled_deps that injects the given mocks."""
    mock_luma_i2c = MagicMock(return_value=MagicMock())
    mock_ssd1306 = MagicMock(return_value=mock_device)

    mock_Image = MagicMock()
    mock_Image.new.return_value = mock_image

    mock_ImageDraw = MagicMock()
    mock_ImageDraw.Draw.return_value = mock_draw

    mock_ImageFont = MagicMock()
    mock_ImageFont.load_default.return_value = mock_font

    return patch(
        "raspbot.display.oled._import_oled_deps",
        return_value=(mock_luma_i2c, mock_ssd1306, mock_Image, mock_ImageDraw, mock_ImageFont),
    )


class TestOLEDDisplay:
    def test_begin_returns_true_on_success(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            assert oled.begin() is True

    def test_begin_returns_false_on_exception(self) -> None:
        with patch("raspbot.display.oled._import_oled_deps", side_effect=ImportError("no luma")):
            oled = OLEDDisplay()
            assert oled.begin() is False

    def test_begin_initialises_internal_state(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
        assert oled._device is mock_device
        assert oled._image is mock_image
        assert oled._draw is mock_draw
        assert oled._font is mock_font

    def test_clear_calls_rectangle(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.clear()
        mock_draw.rectangle.assert_called_once_with(
            (0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0
        )

    def test_clear_with_refresh_calls_display(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.clear(refresh=True)
        mock_device.display.assert_called_once_with(mock_image)

    def test_clear_without_refresh_does_not_call_display(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.clear(refresh=False)
        mock_device.display.assert_not_called()

    def test_add_text_calls_draw_text(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.add_text(0, 0, "hello")
        mock_draw.text.assert_called_once_with((0, 0), "hello", font=mock_font, fill=255)

    def test_add_text_out_of_bounds_is_ignored(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.add_text(200, 200, "off screen")
        mock_draw.text.assert_not_called()

    def test_add_line_maps_to_correct_y(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.add_line("row2", line=2)
        # line 2 -> y = 8 * (2-1) = 8
        mock_draw.text.assert_called_once_with((0, 8), "row2", font=mock_font, fill=255)

    def test_add_line_out_of_range_is_ignored(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.add_line("bad", line=5)
        mock_draw.text.assert_not_called()

    def test_refresh_calls_device_display(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            oled = OLEDDisplay()
            oled.begin()
            oled.refresh()
        mock_device.display.assert_called_once_with(mock_image)

    def test_methods_raise_before_begin(self) -> None:
        oled = OLEDDisplay()
        with pytest.raises(OLEDError):
            oled.clear()
        with pytest.raises(OLEDError):
            oled.add_text(0, 0, "x")
        with pytest.raises(OLEDError):
            oled.refresh()

    def test_context_manager_calls_begin_and_clears_on_exit(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font):
            with OLEDDisplay() as oled:
                assert oled._device is mock_device
            # clear(refresh=True) on exit -> display() must have been called
            mock_device.display.assert_called()

    def test_context_manager_exit_suppresses_oled_error(self) -> None:
        mock_device, mock_image, mock_draw, mock_font = _make_oled_mocks()
        with _patch_deps(mock_device, mock_image, mock_draw, mock_font), OLEDDisplay() as oled:
            # Simulate device going away after begin
            oled._device = None
        # No exception should propagate out of the with block


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------


class TestButton:
    def test_is_pressed_returns_true_when_register_is_1(self, mock_bus: MagicMock) -> None:
        mock_bus.read_block_data.return_value = [1]
        btn = Button(mock_bus)
        assert btn.is_pressed() is True

    def test_is_pressed_returns_false_when_register_is_0(self, mock_bus: MagicMock) -> None:
        mock_bus.read_block_data.return_value = [0]
        btn = Button(mock_bus)
        assert btn.is_pressed() is False

    def test_is_pressed_reads_correct_register(self, mock_bus: MagicMock) -> None:
        mock_bus.read_block_data.return_value = [0]
        btn = Button(mock_bus)
        btn.is_pressed()
        mock_bus.read_block_data.assert_called_once_with(Reg.BUTTON, 1)


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------


def _fake_frame() -> MagicMock:
    """Return a MagicMock that looks enough like a numpy ndarray for our tests."""
    frame = MagicMock()
    frame.shape = (480, 640, 3)
    frame.ndim = 3
    return frame


def _make_mock_cap(
    *,
    is_open: bool = True,
    read_ret: bool = True,
    read_frame: Any = None,
) -> MagicMock:
    """Build a MagicMock that behaves like a cv2.VideoCapture object."""
    if read_frame is None:
        read_frame = _fake_frame()

    cap = MagicMock()
    cap.isOpened.return_value = is_open
    cap.read.return_value = (read_ret, read_frame if read_ret else None)

    # Make get() return sensible defaults for width / height / fps
    # Prop constants match the mock_cv2 values set in _patch_cv2:
    # CAP_PROP_FRAME_WIDTH=3, CAP_PROP_FRAME_HEIGHT=4, CAP_PROP_FPS=5
    def _cap_get(prop: int) -> float:
        return {3: 640.0, 4: 480.0, 5: 30.0}.get(prop, 0.0)

    cap.get.side_effect = _cap_get
    return cap


def _patch_cv2(mock_cap: MagicMock) -> Any:
    """Return a patcher that replaces _import_cv2 with a mock cv2 module."""
    mock_cv2 = MagicMock()
    mock_cv2.VideoCapture.return_value = mock_cap
    mock_cv2.CAP_PROP_FRAME_WIDTH = 3
    mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
    mock_cv2.CAP_PROP_FPS = 5
    mock_cv2.COLOR_BGR2RGB = 4  # arbitrary constant
    return patch("raspbot.camera.opencv_camera._import_cv2", return_value=mock_cv2)


class TestCamera:
    def test_open_returns_true_on_success(self) -> None:
        mock_cap = _make_mock_cap()
        with _patch_cv2(mock_cap):
            cam = Camera()
            assert cam.open() is True

    def test_open_returns_false_when_cap_not_opened(self) -> None:
        mock_cap = _make_mock_cap(is_open=False)
        with _patch_cv2(mock_cap):
            cam = Camera()
            assert cam.open() is False

    def test_open_returns_false_when_cv2_missing(self) -> None:
        with patch(
            "raspbot.camera.opencv_camera._import_cv2",
            side_effect=ImportError("no cv2"),
        ):
            cam = Camera()
            assert cam.open() is False

    def test_is_open_false_before_open(self) -> None:
        cam = Camera()
        assert cam.is_open is False

    def test_is_open_true_after_open(self) -> None:
        mock_cap = _make_mock_cap()
        with _patch_cv2(mock_cap):
            cam = Camera()
            cam.open()
        assert cam.is_open is True

    def test_close_releases_cap(self) -> None:
        mock_cap = _make_mock_cap()
        with _patch_cv2(mock_cap):
            cam = Camera()
            cam.open()
            cam.close()
        mock_cap.release.assert_called_once()
        assert cam._cap is None

    def test_close_is_safe_when_not_open(self) -> None:
        cam = Camera()
        cam.close()  # should not raise

    def test_read_frame_returns_the_captured_object(self) -> None:
        expected = _fake_frame()
        mock_cap = _make_mock_cap(read_frame=expected)
        with _patch_cv2(mock_cap):
            cam = Camera()
            cam.open()
            frame = cam.read_frame()
        # The wrapper must return exactly the object from cap.read()
        assert frame is expected

    def test_read_frame_shape_is_propagated(self) -> None:
        expected = _fake_frame()
        mock_cap = _make_mock_cap(read_frame=expected)
        with _patch_cv2(mock_cap):
            cam = Camera()
            cam.open()
            frame = cam.read_frame()
        assert frame is not None
        assert frame.shape == (480, 640, 3)

    def test_read_frame_returns_none_when_cap_fails(self) -> None:
        mock_cap = _make_mock_cap(read_ret=False)
        with _patch_cv2(mock_cap):
            cam = Camera()
            cam.open()
            frame = cam.read_frame()
        assert frame is None

    def test_read_frame_raises_when_not_open(self) -> None:
        cam = Camera()
        with pytest.raises(RuntimeError, match="not open"):
            cam.read_frame()

    def test_read_frame_rgb_calls_cvt_color(self) -> None:
        expected = _fake_frame()
        mock_cap = _make_mock_cap()
        mock_cv2 = MagicMock()
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5
        mock_cv2.COLOR_BGR2RGB = 4
        mock_cv2.cvtColor.return_value = expected

        with patch("raspbot.camera.opencv_camera._import_cv2", return_value=mock_cv2):
            cam = Camera()
            cam.open()
            result = cam.read_frame_rgb()

        mock_cv2.cvtColor.assert_called_once()
        assert result is expected

    def test_read_frame_rgb_returns_none_when_cap_fails(self) -> None:
        mock_cap = _make_mock_cap(read_ret=False)
        with _patch_cv2(mock_cap):
            cam = Camera()
            cam.open()
            assert cam.read_frame_rgb() is None

    def test_context_manager_opens_and_closes(self) -> None:
        mock_cap = _make_mock_cap()
        with _patch_cv2(mock_cap), Camera() as cam:
            assert cam.is_open is True
        mock_cap.release.assert_called_once()

    def test_width_height_fps_properties(self) -> None:
        mock_cap = _make_mock_cap()
        with _patch_cv2(mock_cap):
            cam = Camera(width=320, height=240, fps=15)
            cam.open()
            # get() side_effect returns 640/480/30 for the standard props
            assert cam.width == 640
            assert cam.height == 480
            assert cam.fps == 30.0

    def test_width_height_zero_when_not_open(self) -> None:
        cam = Camera()
        assert cam.width == 0
        assert cam.height == 0
        assert cam.fps == 0.0

    def test_repr_shows_status(self) -> None:
        cam = Camera(device=1)
        r = repr(cam)
        assert "device=1" in r
        assert "closed" in r
