"""
SSD1306 OLED display module.

Provides a clean interface for the 128×32 SSD1306 OLED display used on the
Yahboom Raspbot V2.  Uses ``luma.oled`` as the hardware driver and Pillow for
framebuffer rendering.

This module is an **optional extra** — install the ``oled`` extras group::

    pip install "raspbot[oled]"

Attempting to import without the optional dependencies raises :class:`ImportError`
with a helpful message.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from raspbot.exceptions import OLEDError

logger = logging.getLogger(__name__)

# Width/height constants for the default 128×32 panel
OLED_WIDTH = 128
OLED_HEIGHT = 32
_LINE_HEIGHT = 8   # pixels per text line (4 lines fit on 32 px)
_NUM_LINES = OLED_HEIGHT // _LINE_HEIGHT  # 4


def _import_oled_deps() -> tuple:
    """Lazily import optional OLED dependencies and return the needed symbols."""
    try:
        from luma.core.interface.serial import i2c as luma_i2c
        from luma.oled.device import ssd1306
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise ImportError(
            "OLED support requires additional packages. "
            'Install them with: pip install "raspbot[oled]"'
        ) from exc
    return luma_i2c, ssd1306, Image, ImageDraw, ImageFont


class OLEDDisplay:
    """128×32 SSD1306 OLED display controller.

    The display is **not** initialised until :meth:`begin` is called,
    making import-time side-effect free.

    Parameters
    ----------
    i2c_port:
        Linux I2C bus number (default 1).
    i2c_address:
        I2C address of the SSD1306 (default ``0x3C``).
    """

    def __init__(self, i2c_port: int = 1, i2c_address: int = 0x3C) -> None:
        self._port = i2c_port
        self._address = i2c_address
        self._device: object | None = None
        self._image: object | None = None
        self._draw: object | None = None
        self._font: object | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def begin(self) -> bool:
        """Initialise the OLED hardware.

        Returns
        -------
        bool
            ``True`` on success, ``False`` if the display cannot be found.
        """
        try:
            luma_i2c, ssd1306, Image, ImageDraw, ImageFont = _import_oled_deps()
            serial = luma_i2c(port=self._port, address=self._address)
            self._device = ssd1306(serial, width=OLED_WIDTH, height=OLED_HEIGHT)
            self._image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
            self._draw = ImageDraw.Draw(self._image)
            self._font = ImageFont.load_default()
            logger.debug("OLED initialised (port=%d addr=0x%02X)", self._port, self._address)
            return True
        except Exception as exc:
            logger.warning("OLED not found: %s", exc)
            return False

    def _ensure_ready(self) -> None:
        if self._device is None or self._draw is None:
            raise OLEDError("Display not initialised — call begin() first")

    # ------------------------------------------------------------------
    # Drawing primitives
    # ------------------------------------------------------------------

    def clear(self, refresh: bool = False) -> None:
        """Blank the display buffer.

        Parameters
        ----------
        refresh:
            If ``True``, immediately push the blank frame to the display.
        """
        self._ensure_ready()
        assert self._draw is not None  # for type checkers
        self._draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)
        if refresh:
            self.refresh()

    def add_text(self, x: int, y: int, text: str, refresh: bool = False) -> None:
        """Draw *text* at pixel coordinates (*x*, *y*).

        Coordinates outside the 128×32 panel are silently ignored.

        Parameters
        ----------
        x, y:
            Pixel position (origin = top-left).
        text:
            String to render.
        refresh:
            Push to display immediately if ``True``.
        """
        self._ensure_ready()
        assert self._draw is not None and self._font is not None
        if 0 <= x < OLED_WIDTH and 0 <= y < OLED_HEIGHT:
            self._draw.text((x, y), str(text), font=self._font, fill=255)
        if refresh:
            self.refresh()

    def add_line(self, text: str, line: int = 1, refresh: bool = False) -> None:
        """Write *text* to one of the four logical display lines.

        Parameters
        ----------
        text:
            String to render (long strings are not automatically wrapped).
        line:
            Line number 1–4 (1 = top).
        refresh:
            Push to display immediately if ``True``.
        """
        if not 1 <= line <= _NUM_LINES:
            logger.warning("add_line: line %d out of range (1–%d)", line, _NUM_LINES)
            return
        y = _LINE_HEIGHT * (line - 1)
        self.add_text(0, y, text, refresh)

    def refresh(self) -> None:
        """Push the current framebuffer to the physical OLED display."""
        self._ensure_ready()
        assert self._device is not None and self._image is not None
        # luma.oled devices expose a display() method that accepts a PIL image
        self._device.display(self._image)  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "OLEDDisplay":
        self.begin()
        return self

    def __exit__(self, *_: object) -> None:
        try:
            self.clear(refresh=True)
        except OLEDError:
            pass
