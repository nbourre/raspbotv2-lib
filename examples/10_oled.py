"""
10_oled.py - SSD1306 128x32 OLED display

Requires the optional OLED extra:
    pip install "raspbot[oled]"

Demonstrates OLEDDisplay methods:
  - begin()       initialise hardware (returns False if not found)
  - clear()       blank the framebuffer (refresh=True to push immediately)
  - add_text()    draw text at a pixel coordinate (x, y)
  - add_line()    draw text on one of the 4 logical 8-pixel lines
  - refresh()     push the current framebuffer to the display
  - context manager  auto-begin on entry, auto-clear on exit

The display is 128 x 32 pixels with 4 text lines of 8 pixels each.

Run on Raspberry Pi with the SSD1306 wired to I2C bus 1 (address 0x3C).
"""

import time

from raspbot.display.oled import OLEDDisplay

# OLEDDisplay is independent of Robot -- create it directly.
# Pass i2c_port and i2c_address if your wiring differs from the defaults.
with OLEDDisplay(i2c_port=1, i2c_address=0x3C) as oled:
    # ------------------------------------------------------------------
    # add_line() -- write to one of the 4 logical lines (1-4, top to bottom)
    # ------------------------------------------------------------------

    print("Writing 4 lines ...")
    oled.clear()
    oled.add_line("raspbot v2", line=1)
    oled.add_line("OLED example", line=2)
    oled.add_line("128 x 32 px", line=3)
    oled.add_line("4 text lines", line=4)
    oled.refresh()
    time.sleep(2)

    # ------------------------------------------------------------------
    # clear() + refresh -- blank the display
    # ------------------------------------------------------------------

    print("Clearing ...")
    oled.clear(refresh=True)
    time.sleep(0.5)

    # ------------------------------------------------------------------
    # add_text() -- arbitrary pixel coordinates
    # ------------------------------------------------------------------

    print("Pixel-level text placement ...")
    oled.add_text(0, 0, "x=0, y=0")
    oled.add_text(40, 12, "x=40,y=12")
    oled.add_text(0, 24, "x=0, y=24")
    oled.refresh()
    time.sleep(2)

    # ------------------------------------------------------------------
    # Dynamic update loop -- update a single line each iteration
    # ------------------------------------------------------------------

    print("Countdown ...")
    for i in range(5, 0, -1):
        oled.clear()
        oled.add_line("Countdown:", line=1)
        oled.add_line(str(i), line=3)
        oled.refresh()
        time.sleep(1)

    oled.clear(refresh=True)

# Context manager __exit__ clears the display automatically.
print("Done.")
