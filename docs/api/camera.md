# Camera

`raspbot.camera.opencv_camera.Camera`

OpenCV `VideoCapture` wrapper for the Raspbot V2.

!!! warning "Optional extra"
    This module requires the `camera` extras group:

    ```bash
    pip install "raspbot[camera]"
    ```

    All methods that need `cv2` raise `ImportError` with a helpful message if it is not installed.

Access via `Robot.camera`.

---

## Constructor

```python
class Camera:
    def __init__(
        self,
        device: int | str = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
    ) -> None: ...
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `device` | `int` or `str` | `0` | Camera index or device path (e.g. `"/dev/video0"`) |
| `width` | `int` | `640` | Requested capture width (driver may differ) |
| `height` | `int` | `480` | Requested capture height (driver may differ) |
| `fps` | `int` | `30` | Requested frame rate (driver may differ) |

The capture device is **not** opened until `open()` is called.

---

## Properties

### `is_open`

```python
@property
def is_open(self) -> bool
```

`True` when the capture device is open and ready.

### `width`

```python
@property
def width(self) -> int
```

Actual capture width reported by the driver (0 when not open).

### `height`

```python
@property
def height(self) -> int
```

Actual capture height reported by the driver (0 when not open).

### `fps`

```python
@property
def fps(self) -> float
```

Actual FPS reported by the driver (0 when not open).

---

## Methods

### `open()`

```python
def open(self) -> bool
```

Open the capture device.

**Returns:** `True` on success, `False` if the device cannot be opened (not connected, driver not
loaded, or `cv2` not installed).

---

### `close()`

```python
def close(self) -> None
```

Release the capture device. Safe to call even if the device is already closed.

---

### `read_frame()`

```python
def read_frame(self) -> numpy.ndarray | None
```

Capture one frame from the camera.

**Returns:** A BGR image array with shape `(height, width, 3)` and dtype `uint8`, or `None` if
the frame could not be read.

**Raises:** `RuntimeError` if the camera has not been opened first.

---

### `read_frame_rgb()`

```python
def read_frame_rgb(self) -> numpy.ndarray | None
```

Capture one frame and convert from BGR to RGB.

Convenience wrapper for callers that expect RGB order (e.g. for display with matplotlib or Pillow).

---

## Context manager

`Camera` supports the context manager protocol.
`open()` is called on entry, `close()` on exit.

```python
with Camera(device=0) as cam:
    frame = cam.read_frame()
```

---

## Raspberry Pi camera notes

For a Pi Camera Module (V1/V2/3) on Pi OS Bullseye or earlier:

```bash
sudo modprobe bcm2835-v4l2
```

This exposes the camera as `/dev/video0` which OpenCV can open normally.

For Pi OS Bookworm with `libcamera`, use `libcamera-apps` or configure the V4L2 bridge in
`/boot/config.txt`. USB webcams work without extra configuration.

---

## Examples

```python
from raspbot.camera import Camera

with Camera(device=0) as cam:
    frame = cam.read_frame()      # numpy BGR array
    if frame is not None:
        print("Frame shape:", frame.shape)   # e.g. (480, 640, 3)
```

### Live frame loop

```python
import time
from raspbot import Robot, Task

with Robot() as bot:
    if not bot.camera.open():
        raise RuntimeError("Camera not available")

    @Task.every(0.033)  # ~30 fps
    def capture(ct: float) -> None:
        frame = bot.camera.read_frame()
        if frame is not None:
            # process frame ...
            pass

    end = time.monotonic() + 10.0
    while time.monotonic() < end:
        capture(time.monotonic())
        time.sleep(0.001)
```

---

## See also

- [Robot facade](robot.md)
- [Cooperative Tasks guide](../guides/cooperative_tasks.md)
