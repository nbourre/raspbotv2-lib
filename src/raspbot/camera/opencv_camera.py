"""
OpenCV camera wrapper for the Raspbot V2.

Provides a thin, dependency-isolated interface around ``cv2.VideoCapture``
that follows the same lazy-init and optional-dependency patterns used by the
rest of the ``raspbot`` package.

This module is an **optional extra** - install the ``camera`` extras group::

    pip install "raspbot[camera]"

Attempting to use any method without the optional dependencies raises
:class:`ImportError` with a helpful message.

On the Raspberry Pi with a Camera Module, enable the V4L2 driver so that
OpenCV can open it as a standard device::

    # Add to /etc/modules or run once:
    sudo modprobe bcm2835-v4l2          # Pi OS Bullseye and earlier
    # or configure via raspi-config / config.txt for Pi OS Bookworm + libcamera

USB webcams are typically available as ``/dev/video0`` without any extra
configuration.

Example usage::

    from raspbot.camera import Camera

    with Camera(device=0) as cam:
        frame = cam.read_frame()    # numpy ndarray, BGR, shape (H, W, 3)
        if frame is not None:
            # process frame with OpenCV, NumPy, etc.
            pass
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _import_cv2() -> Any:
    """Lazily import cv2 and return the module.

    Raises
    ------
    ImportError
        When ``opencv-python`` (or ``opencv-python-headless``) is not installed.
    """
    try:
        import cv2

        return cv2
    except ImportError as exc:
        raise ImportError(
            'Camera support requires opencv-python. Install it with: pip install "raspbot[camera]"'
        ) from exc


# Default capture resolution -- matches a common Pi Camera / USB webcam mode.
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480


class Camera:
    """OpenCV VideoCapture wrapper for the Raspbot V2.

    The capture device is **not** opened until :meth:`open` is called (or the
    object is used as a context manager), keeping import-time side-effect free.

    Parameters
    ----------
    device:
        Camera index (integer) or device path string (e.g. ``"/dev/video0"``).
        Default is ``0`` (the first available camera).
    width:
        Requested capture width in pixels (default ``640``).  The driver may
        choose a different resolution if the requested one is not supported.
    height:
        Requested capture height in pixels (default ``480``).
    fps:
        Requested capture frame rate (default ``30``).  The driver may choose
        a different rate if the requested one is not supported.

    Attributes
    ----------
    is_open : bool
        ``True`` when the capture device is successfully opened.
    """

    def __init__(
        self,
        device: int | str = 0,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        fps: int = 30,
    ) -> None:
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps
        self._cap: Any = None  # cv2.VideoCapture or None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        """Return ``True`` when the capture device is open and ready."""
        return self._cap is not None and self._cap.isOpened()

    @property
    def width(self) -> int:
        """Actual capture width reported by the driver (0 when not open)."""
        if self._cap is None:
            return 0
        return int(self._cap.get(self._import_cv2_cap_prop("CAP_PROP_FRAME_WIDTH")))

    @property
    def height(self) -> int:
        """Actual capture height reported by the driver (0 when not open)."""
        if self._cap is None:
            return 0
        return int(self._cap.get(self._import_cv2_cap_prop("CAP_PROP_FRAME_HEIGHT")))

    @property
    def fps(self) -> float:
        """Actual FPS reported by the driver (0 when not open)."""
        if self._cap is None:
            return 0.0
        return float(self._cap.get(self._import_cv2_cap_prop("CAP_PROP_FPS")))

    def _import_cv2_cap_prop(self, prop_name: str) -> int:
        """Return the integer value of a cv2 capture property constant."""
        cv2 = _import_cv2()
        return int(getattr(cv2, prop_name))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def open(self) -> bool:
        """Open the capture device.

        Returns
        -------
        bool
            ``True`` on success, ``False`` if the device cannot be opened
            (e.g. not connected, driver not loaded, cv2 not installed).
        """
        try:
            cv2 = _import_cv2()
        except ImportError as exc:
            logger.warning("Camera: cv2 not available: %s", exc)
            return False
        try:
            cap = cv2.VideoCapture(self._device)
            if not cap.isOpened():
                logger.warning("Camera: could not open device %r", self._device)
                return False

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
            cap.set(cv2.CAP_PROP_FPS, self._fps)

            self._cap = cap
            logger.debug(
                "Camera opened: device=%r width=%d height=%d fps=%.1f",
                self._device,
                self.width,
                self.height,
                self.fps,
            )
            return True
        except Exception as exc:  # pragma: no cover
            logger.warning("Camera: exception during open: %s", exc)
            return False

    def close(self) -> None:
        """Release the capture device.

        Safe to call even if the device is already closed.
        """
        if self._cap is not None:
            try:
                self._cap.release()
                logger.debug("Camera released: device=%r", self._device)
            except Exception as exc:  # pragma: no cover
                logger.warning("Camera: exception during close: %s", exc)
            self._cap = None

    # ------------------------------------------------------------------
    # Frame capture
    # ------------------------------------------------------------------

    def read_frame(self) -> Any | None:
        """Capture one frame from the camera.

        Returns
        -------
        numpy.ndarray or None
            A BGR image array with shape ``(height, width, 3)`` and dtype
            ``uint8``, or ``None`` if the frame could not be read (e.g.
            device disconnected, end of file for video sources).

        Raises
        ------
        RuntimeError
            If the camera has not been opened via :meth:`open` first.
        """
        if self._cap is None or not self._cap.isOpened():
            raise RuntimeError(
                "Camera is not open. Call open() (or use as a context manager) first."
            )

        ret: bool
        frame: Any
        ret, frame = self._cap.read()
        if not ret or frame is None:
            logger.debug("Camera: read_frame returned no data (device=%r)", self._device)
            return None

        return frame

    def read_frame_rgb(self) -> Any | None:
        """Capture one frame and convert it from BGR to RGB.

        Convenience wrapper around :meth:`read_frame` for callers that expect
        RGB order (e.g. for display with matplotlib or Pillow).

        Returns
        -------
        numpy.ndarray or None
            An RGB image array, or ``None`` if the frame could not be read.

        Raises
        ------
        RuntimeError
            If the camera has not been opened via :meth:`open` first.
        """
        cv2 = _import_cv2()
        frame = self.read_frame()
        if frame is None:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> Camera:
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __repr__(self) -> str:
        status = "open" if self.is_open else "closed"
        return (
            f"Camera(device={self._device!r}, "
            f"width={self._width}, height={self._height}, "
            f"fps={self._fps}, status={status})"
        )
