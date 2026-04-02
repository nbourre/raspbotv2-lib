"""
Hardware-in-the-loop tests.

These tests require a physical Raspbot V2 connected over I2C.
They are skipped by default and must be run explicitly on the Pi:

    python -m pytest tests/ -m hardware -v

They are intentionally NOT run in CI or on development machines.
"""

from __future__ import annotations

import time
from collections.abc import Generator

import pytest

from raspbot import Robot
from raspbot.display.oled import OLEDDisplay
from raspbot.types import LedColor, MotorId

# ---------------------------------------------------------------------------
# Shared fixture - one Robot instance per test, cleaned up after each test
# ---------------------------------------------------------------------------


@pytest.fixture()
def bot() -> Generator[Robot, None, None]:
    """Open a real Robot connection and close it after the test."""
    robot = Robot()
    yield robot
    robot.close()


# ---------------------------------------------------------------------------
# Smoke tests - verify the device responds without crashing
# ---------------------------------------------------------------------------


@pytest.mark.hardware
def test_robot_opens_and_closes() -> None:
    """Robot can be constructed and closed without raising."""
    with Robot():
        pass


@pytest.mark.hardware
def test_ultrasonic_returns_positive_distance(bot: Robot) -> None:
    """Ultrasonic sensor returns a plausible distance (> 0 mm, < 5 000 mm)."""
    with bot.ultrasonic:
        distance = bot.ultrasonic.read_mm()
    assert 0 < distance < 5000, f"Unexpected distance: {distance} mm"


@pytest.mark.hardware
def test_line_tracker_reads_without_error(bot: Robot) -> None:
    """Line tracker can be read and returns a valid LineState."""
    state = bot.line_tracker.read()
    # All four channels must be boolean
    assert isinstance(state.x1, bool)
    assert isinstance(state.x2, bool)
    assert isinstance(state.x3, bool)
    assert isinstance(state.x4, bool)
    assert 0 <= state.raw <= 0xFF


@pytest.mark.hardware
def test_ir_receiver_enable_disable(bot: Robot) -> None:
    """IR receiver can be enabled, polled, and disabled without error."""
    bot.ir.enable()
    time.sleep(0.1)
    # read_keycode returns int or None - either is valid here
    result = bot.ir.read_keycode()
    assert result is None or isinstance(result, int)
    bot.ir.disable()


@pytest.mark.hardware
def test_button_reads_without_error(bot: Robot) -> None:
    """Button state can be read and returns a bool."""
    state = bot.button.is_pressed()
    assert isinstance(state, bool)


@pytest.mark.hardware
def test_button_not_pressed_by_default(bot: Robot) -> None:
    """Button reports not pressed when no one is touching it."""
    # This assumes the test is run without pressing KEY1.
    assert bot.button.is_pressed() is False


# ---------------------------------------------------------------------------
# Actuator smoke tests - brief on/off to confirm register writes succeed
# ---------------------------------------------------------------------------


@pytest.mark.hardware
def test_buzzer_beeps(bot: Robot) -> None:
    """Buzzer on→off completes without raising."""
    bot.buzzer.beep(0.1)


@pytest.mark.hardware
def test_leds_all_on_then_off(bot: Robot) -> None:
    """All LEDs can be turned on and off."""
    bot.leds.set_all(LedColor.GREEN)
    time.sleep(0.2)
    bot.leds.off_all()


@pytest.mark.hardware
def test_led_single(bot: Robot) -> None:
    """A single LED can be lit and turned off."""
    bot.leds.set_one(0, LedColor.RED)
    time.sleep(0.2)
    bot.leds.off_one(0)


@pytest.mark.hardware
def test_servo_pan_sweeps(bot: Robot) -> None:
    """Pan servo moves to 45°, 90°, 135° without raising."""
    for angle in (45, 90, 135, 90):
        bot.servos.pan.set_angle(angle)
        time.sleep(0.3)


@pytest.mark.hardware
def test_servo_tilt_clamps_at_110(bot: Robot) -> None:
    """Tilt servo accepts 110° (hardware max) without raising."""
    bot.servos.tilt.set_angle(110)
    time.sleep(0.3)
    bot.servos.tilt.set_angle(25)


@pytest.mark.hardware
def test_motors_brief_forward_stop(bot: Robot) -> None:
    """All motors spin forward briefly then stop - robot should move slightly."""
    bot.motors.forward(speed=80)
    time.sleep(0.3)
    bot.motors.stop()


@pytest.mark.hardware
def test_motors_individual_drive(bot: Robot) -> None:
    """Each motor can be driven individually via signed speed."""
    for motor in MotorId:
        bot.motors.drive(motor, 80)
        time.sleep(0.1)
        bot.motors.drive(motor, 0)


# ---------------------------------------------------------------------------
# OLED display tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def oled() -> Generator[OLEDDisplay, None, None]:
    """Open a real OLEDDisplay connection and close it after the test."""
    display = OLEDDisplay()
    started = display.begin()
    if not started:
        pytest.skip("OLED display not found on I2C bus")
    yield display
    display.clear(refresh=True)


@pytest.mark.hardware
def test_oled_begin(oled: OLEDDisplay) -> None:
    """OLEDDisplay.begin() succeeds and the device is ready."""
    # If we reach this point the fixture did not skip, so begin() returned True.
    assert oled._device is not None
    assert oled._draw is not None


@pytest.mark.hardware
def test_oled_clear(oled: OLEDDisplay) -> None:
    """clear() blanks the display without raising."""
    oled.clear(refresh=True)


@pytest.mark.hardware
def test_oled_add_text(oled: OLEDDisplay) -> None:
    """add_text() draws a string at given pixel coordinates."""
    oled.clear()
    oled.add_text(0, 0, "Hello Pi", refresh=True)
    time.sleep(0.5)


@pytest.mark.hardware
def test_oled_add_line_all_four_lines(oled: OLEDDisplay) -> None:
    """All four logical lines can be written and displayed."""
    oled.clear()
    for i in range(1, 5):
        oled.add_line(f"Line {i}", line=i)
    oled.refresh()
    time.sleep(1.0)


@pytest.mark.hardware
def test_oled_add_line_out_of_range_does_not_raise(oled: OLEDDisplay) -> None:
    """add_line() with an out-of-range line number is silently ignored."""
    oled.add_line("ignored", line=0)
    oled.add_line("ignored", line=5)


@pytest.mark.hardware
def test_oled_refresh(oled: OLEDDisplay) -> None:
    """refresh() pushes the framebuffer to the display without raising."""
    oled.add_line("Refresh test", line=1)
    oled.refresh()
    time.sleep(0.3)


@pytest.mark.hardware
def test_oled_context_manager() -> None:
    """OLEDDisplay used as a context manager initialises and clears cleanly."""
    with OLEDDisplay() as display:
        display.add_line("Context", line=1)
        display.add_line("Manager", line=2)
        display.refresh()
        time.sleep(0.5)
    # After __exit__ the display should be cleared (no exception expected)
