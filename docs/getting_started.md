# Getting Started

This page walks you through everything you need to get `raspbot` running on your Raspberry Pi.

---

## Hardware requirements

- Yahboom Raspbot V2 robot car (fully assembled)
- Raspberry Pi 3B / 4B / 5 (or compatible)
- Raspberry Pi OS (Bullseye or Bookworm, 32-bit or 64-bit)
- USB-C or barrel-jack power supply for the robot chassis

---

## Enable I2C on the Raspberry Pi

The library communicates with the robot's microcontroller over I2C bus 1.

```bash
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable
```

Reboot after enabling.

Verify the bus is up and the robot is detected:

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

You should see address `0x2B` in the output (the Raspbot V2 microcontroller).
If you have the OLED display connected you will also see `0x3C`.

---

## Add your user to the i2c group

To use I2C without `sudo`:

```bash
sudo usermod -aG i2c $USER
# Log out and back in (or reboot) for the change to take effect.
```

---

## Install raspbot

Install the core library:

```bash
pip install raspbot
```

Install optional extras as needed:

```bash
pip install "raspbot[oled]"          # SSD1306 OLED display support
pip install "raspbot[camera]"        # OpenCV camera support
pip install "raspbot[oled,camera]"   # all optional hardware
```

To build the documentation locally:

```bash
pip install "raspbot[docs]"
mkdocs serve
```

---

## Verify the installation

Run this short script on the Pi to confirm I2C communication is working:

```python
from raspbot import Robot

with Robot() as bot:
    print("Robot initialised OK")
    print("Ultrasonic:", bot.ultrasonic.read_cm(), "cm")
```

If you see a distance reading (even `0 cm` before enabling the sensor is fine), the library is
working.

---

## I2C wiring reference

The Raspbot V2 uses the standard Raspberry Pi I2C header pins.
No additional wiring is required -- the microcontroller is on the chassis PCB.

| Signal | Pi GPIO header pin |
|---|---|
| SDA | Pin 3 (GPIO 2) |
| SCL | Pin 5 (GPIO 3) |
| GND | Pin 6 (or any GND) |
| 3.3 V | Pin 1 (or any 3.3 V) |

The robot's PCB connects directly to the 40-pin header; no jumper wires are needed in the
standard Yahboom assembly.

---

## First program

Save this as `hello_robot.py` on your Pi and run it with `python hello_robot.py`:

```python
import time
from raspbot import Robot
from raspbot.types import LedColor

with Robot() as bot:
    # Say hello with LEDs and buzzer
    bot.leds.set_all(LedColor.GREEN)
    bot.buzzer.beep(0.1)

    # Drive forward for one second
    bot.motors.forward(speed=150)
    time.sleep(1)
    bot.motors.stop()

    # Read a distance measurement
    print("Distance:", bot.ultrasonic.read_cm(), "cm")

    # Turn off LEDs
    bot.leds.off_all()

print("Done.")
```

---

## Next steps

- [API Reference -- Robot](api/robot.md) -- the main facade class
- [API Reference -- Motors](api/motors.md) -- motor control
- [Cooperative Tasks guide](guides/cooperative_tasks.md) -- non-blocking loops
- [Troubleshooting](guides/troubleshooting.md) -- common problems
