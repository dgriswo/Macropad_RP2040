# Macropad RP2040 with multiple keymaps

Designed for use with Adafruit's Macropad RP2040: https://www.adafruit.com/product/5128


## Requirements:
* CircuitPython 7.0.0-alpha.3 or later
* neopixel
* adafruit_displayio_sh1106
* adafruit_hid
* adafruit_bus_device
* adafruit_display_text

## Mulitple keymaps

Multiple key maps are stored in keymaps.py as Python dictionaries containing tuples of (macro,description).  Either string, Keycodes, or lists of Keycodes are supported.

Even if there is no macro or name for a given key, a blank entry needs to exist for proper parsing.

## Images

<br>
<img src="https://user-images.githubusercontent.com/15717486/124365153-2994b400-dc14-11eb-85f9-4a065d34484c.jpg" width="504" height="672"><br>
<img src="https://user-images.githubusercontent.com/15717486/124365156-2b5e7780-dc14-11eb-949f-a4043af543a1.jpg" width="504" height="672"><br>
<img src="https://user-images.githubusercontent.com/15717486/124365159-2dc0d180-dc14-11eb-8f01-40e6960cf2fe.jpg" width="504" height="672"><br>
