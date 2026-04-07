# Troubleshooting

Common problems and how to fix them.

---

## I2C / hardware issues

### `DeviceNotFoundError: No device at I2C address 0x2B on bus 1`

The robot's microcontroller was not found on the I2C bus.

**Checklist:**

1. Is I2C enabled?
   ```bash
   sudo raspi-config   # Interface Options > I2C > Enable, then reboot
   ```

2. Is the robot powered on?
   The Raspbot V2 requires its own power supply (batteries or DC barrel jack).
   The Pi's 5 V USB supply alone is not sufficient.

3. Can the device be detected?
   ```bash
   sudo apt install -y i2c-tools
   i2cdetect -y 1
   ```
   You should see `2b` at the intersection of row 20, column b.
   If not, check power and the physical 40-pin header connection.

---

### `PermissionError: [Errno 13] Permission denied: '/dev/i2c-1'`

Your user account does not have access to the I2C device.

```bash
sudo usermod -aG i2c $USER
# Log out and log back in, or reboot.
```

Verify with:
```bash
groups   # should include 'i2c'
```

---

### Motors don't move (servos/buzzer work fine)

The motors need a separate power rail.
If the robot is running on USB power from the Pi, the motors will be under-powered.

- Connect the robot's battery pack or a suitable 5-12 V supply.
- Confirm the power switch on the chassis PCB is in the ON position.

---

### Ultrasonic sensor always returns 0

1. Did you call `enable()` first (or use the context manager)?
   ```python
   bot.ultrasonic.enable()   # waits 60 ms for warmup
   dist = bot.ultrasonic.read_mm()
   ```
2. Is there an object within range?
   The HC-SR04 has a typical range of 2 cm - 400 cm.
   At very short distances (< 2 cm) the reading is unreliable.

---

### Line tracker reads all zeros

1. Check that the sensor array is facing down towards the floor/track.
2. Verify adequate lighting -- IR sensors can be confused by bright IR sources.
3. Confirm the track is high-contrast (black tape on white/light surface).
4. Print the raw byte for debugging:
   ```python
   state = bot.line_tracker.read()
   print(f"raw=0x{state.raw:02X}  {state}")
   ```

---

## OLED display

### `ImportError: OLED support requires additional packages`

Install the optional extra:

```bash
pip install "raspbot[oled]"
```

### OLED display shows nothing after `begin()`

1. Check the I2C address. The default is `0x3C`.
   ```bash
   i2cdetect -y 1   # look for 3c in the output
   ```
   If it is at `0x3D`, create the display with `OLEDDisplay(i2c_address=0x3D)`.

2. Did you call `refresh()` after drawing?
   ```python
   oled.add_line("Hello!", line=1)
   oled.refresh()   # <-- required to push to the physical display
   ```

---

## Camera

### `ImportError: Camera support requires opencv-python`

Install the optional extra:

```bash
pip install "raspbot[camera]"
```

### `camera.open()` returns `False`

1. Is the camera connected?
   ```bash
   ls /dev/video*   # should show /dev/video0 or similar
   v4l2-ctl --list-devices
   ```

2. For Pi Camera Module on Bookworm: ensure the V4L2 driver is configured.
   See the [Camera API reference](../api/camera.md) for details.

3. Is another process using the camera?
   ```bash
   sudo fuser /dev/video0
   ```

### `RuntimeError: Camera is not open`

You called `read_frame()` without calling `open()` first:

```python
if bot.camera.open():
    frame = bot.camera.read_frame()
```

Or use the context manager:

```python
with bot.camera:
    frame = bot.camera.read_frame()
```

---

## Python / package issues

### `ModuleNotFoundError: No module named 'raspbot'`

The package is not installed in the active Python environment:

```bash
pip install raspbot
# or from source:
pip install -e .
```

If using a virtual environment, make sure it is activated.

### `mypy` or LSP reports errors on `raspbot` imports

If you are developing on Windows and remoting to the Pi, the LSP server runs on Windows where
`smbus2` and `luma.oled` are not installed.
These are false positives -- the code runs correctly on the Pi.
Ignore them, or add the Pi's site-packages to the LSP's Python path.

---

## Running hardware tests

Hardware tests are skipped by default.
To run them on the actual robot:

```bash
pytest -m hardware
```

These tests require a Raspbot V2 to be physically connected and powered on.

---

## See also

- [Getting Started](../getting_started.md)
- [Exceptions API reference](../api/exceptions.md)
- [Migration Guide](migration.md)
