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
from raspbot.display.oled import OLED_HEIGHT, OLED_WIDTH, OLEDDisplay
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

    def test_beep_calls_on_then_off(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        with patch("raspbot.actuators.buzzer.time.sleep"):
            b.beep(0.1)
        calls = mock_bus.write_block_data.call_args_list
        assert calls[0] == call(Reg.BEEP, [1])
        assert calls[1] == call(Reg.BEEP, [0])

    def test_pattern_repeats(self, mock_bus: MagicMock) -> None:
        b = Buzzer(mock_bus)
        with patch("raspbot.actuators.buzzer.time.sleep"):
            b.pattern(0.1, 0.1, 3)
        # 3 beeps x 2 calls (on + off) = 6
        assert mock_bus.write_block_data.call_count == 6


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
        with patch(
            "raspbot.display.oled._import_oled_deps", side_effect=ImportError("no luma")
        ):
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
    def test_is_pressed_returns_true_when_register_is_1(
        self, mock_bus: MagicMock
    ) -> None:
        mock_bus.read_block_data.return_value = [1]
        btn = Button(mock_bus)
        assert btn.is_pressed() is True

    def test_is_pressed_returns_false_when_register_is_0(
        self, mock_bus: MagicMock
    ) -> None:
        mock_bus.read_block_data.return_value = [0]
        btn = Button(mock_bus)
        assert btn.is_pressed() is False

    def test_is_pressed_reads_correct_register(self, mock_bus: MagicMock) -> None:
        mock_bus.read_block_data.return_value = [0]
        btn = Button(mock_bus)
        btn.is_pressed()
        mock_bus.read_block_data.assert_called_once_with(Reg.BUTTON, 1)
