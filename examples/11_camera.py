"""
11_camera.py - OpenCV camera capture

Requires the optional camera extra:
    pip install "raspbot[camera]"

Demonstrates Camera methods:
  - open()             open the capture device (returns False if unavailable)
  - close()            release the device
  - is_open            property -- True when device is open and ready
  - width / height     actual resolution reported by the driver
  - fps                actual frame rate reported by the driver
  - read_frame()       capture one BGR ndarray (H, W, 3) or None
  - read_frame_rgb()   capture one RGB ndarray (H, W, 3) or None
  - context manager    auto-open / auto-close

On Raspberry Pi with the Camera Module, enable the V4L2 driver first:
    sudo modprobe bcm2835-v4l2          # Pi OS Bullseye and earlier
  or configure via raspi-config for Pi OS Bookworm + libcamera.

USB webcams are typically /dev/video0 without extra configuration.

Run on Raspberry Pi with a camera attached.
"""

import sys
import time

from raspbot.camera import Camera

# ------------------------------------------------------------------
# Basic open / read_frame / close
# ------------------------------------------------------------------

print("Opening camera at device 0 ...")
cam = Camera(device=0, width=640, height=480, fps=30)

if not cam.open():
    print("ERROR: could not open camera. Check the device is connected.")
    sys.exit(1)

print(f"Opened: {cam.width} x {cam.height} px at {cam.fps:.1f} fps")

print("Capturing 10 frames ...")
for i in range(10):
    frame = cam.read_frame()  # BGR ndarray, shape (H, W, 3)
    if frame is None:
        print(f"  Frame {i}: read failed")
    else:
        print(f"  Frame {i}: shape={frame.shape}  dtype={frame.dtype}")
    time.sleep(0.1)

cam.close()
print(f"Camera closed -- is_open={cam.is_open}")

# ------------------------------------------------------------------
# Context manager (recommended) -- auto-opens and auto-closes
# ------------------------------------------------------------------

print("\nUsing context manager ...")
with Camera(device=0) as cam:
    if not cam.is_open:
        print("Camera not available -- skipping.")
    else:
        # read_frame_rgb() returns RGB order instead of OpenCV's default BGR.
        # Useful when passing frames to matplotlib, Pillow, or similar tools.
        frame_rgb = cam.read_frame_rgb()
        if frame_rgb is not None:
            print(f"RGB frame: shape={frame_rgb.shape}")

# ------------------------------------------------------------------
# Minimal processing example -- measure brightness of each frame
# ------------------------------------------------------------------

print("\nBrightness measurement over 5 frames ...")
with Camera(device=0) as cam:
    if cam.is_open:
        for _ in range(5):
            frame = cam.read_frame()
            if frame is not None:
                # frame is a numpy ndarray -- any numpy/cv2 operation works.
                mean_brightness = frame.mean()
                print(f"  Mean pixel value: {mean_brightness:.1f}")
            time.sleep(0.1)

print("Done.")
