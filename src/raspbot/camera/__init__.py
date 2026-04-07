"""
Camera subpackage for the Raspbot V2.

Exports :class:`~raspbot.camera.opencv_camera.Camera` -- an OpenCV
VideoCapture wrapper that follows the same lazy-init pattern used by the rest
of the library.

Install the optional dependency group to use this subpackage::

    pip install "raspbot[camera]"
"""

from __future__ import annotations

from raspbot.camera.opencv_camera import Camera

__all__ = ["Camera"]
