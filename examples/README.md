# raspbot examples

Stand-alone scripts that demonstrate every public class in the `raspbot`
package.  Each file is self-contained and runnable as-is on a Raspberry Pi
with the Raspbot V2 powered on.

## Prerequisites

```bash
# Core library (motors, servos, buzzer, LEDs, sensors, button, Task)
pip install raspbot

# OLED display (example 10)
pip install "raspbot[oled]"

# Camera / OpenCV (example 11)
pip install "raspbot[camera]"
```

Enable I2C and add your user to the `i2c` group if you have not already:

```bash
sudo raspi-config          # Interface Options -> I2C -> Enable
sudo usermod -aG i2c $USER
# Log out and back in for the group change to take effect
```

## Running an example

```bash
python examples/01_motors.py
```

## Index

| File | Class(es) demonstrated | Requires |
|------|------------------------|----------|
| `01_motors.py` | `Motors` -- `forward`, `backward`, `turn_left`, `turn_right`, `stop`, `set`, `drive` | core |
| `02_servos.py` | `Servo`, `ServoPair` -- `set_angle`, `home`, `max_angle` | core |
| `03_buzzer.py` | `Buzzer` -- `on`, `off`, `beep`, `pattern` | core |
| `04_leds.py` | `LedBar` -- `set_all`, `set_one`, `off_all`, `off_one`, `set_brightness_all`, `set_brightness_one`, `count` | core |
| `05_led_effects.py` | `LightEffects` -- `river`, `breathing`, `random_running`, `starlight`, `gradient`, `off`, `stop` | core |
| `06_ultrasonic.py` | `UltrasonicSensor` -- `enable`, `disable`, `read_mm`, `read_cm`, context manager | core |
| `07_line_tracker.py` | `LineTracker`, `LineState` -- `read`, `on_line`, `centered`, `x1`-`x4`, `raw` | core |
| `08_ir_receiver.py` | `IRReceiver` -- `enable`, `disable`, `read_keycode`, context manager | core |
| `09_button.py` | `Button` -- `is_pressed` | core |
| `10_oled.py` | `OLEDDisplay` -- `begin`, `clear`, `add_text`, `add_line`, `refresh`, context manager | `[oled]` |
| `11_camera.py` | `Camera` -- `open`, `close`, `is_open`, `width`, `height`, `fps`, `read_frame`, `read_frame_rgb`, context manager | `[camera]` |
| `12_task_cooperative.py` | `Task` -- constructor, `Task.every` decorator, `rate`, `reset` | core (no hardware) |
| `13_robot_complete.py` | `Robot` + all subsystems in a single non-blocking event loop | core |

## Notes

- All examples use `with Robot() as bot:` (context manager) so that motors
  are stopped and I2C is released cleanly on exit or `Ctrl+C`.
- `12_task_cooperative.py` requires no hardware -- run it on any machine
  to understand the `Task` cooperative multitasking pattern.
- `13_robot_complete.py` is the most complete example: it shows how to
  combine sensors, actuators, and `Task` into a non-blocking control loop.
