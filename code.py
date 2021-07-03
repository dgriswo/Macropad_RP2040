# Credits
# Adapted from the following Adafruit guides:
# rotaryio and keypad: https://learn.adafruit.com/adafruit-macropad-rp2040/keypad
# OLED: https://learn.adafruit.com/adafruit-128x64-oled-featherwing/circuitpython
# neopixel rainbow wheel: https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython


import board
import digitalio
import microcontroller
import rotaryio
import neopixel
import time
import keypad
import usb_hid
import terminalio
import displayio
import busio

from adafruit_display_text import label
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_displayio_sh1106 import SH1106

from keymaps import key_maps

PIXEL_NUM = 12
PIXEL_ORDER = neopixel.GRB
PIXEL_BRIGHTNESS = 0.25

OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_BORDER = 1

# Setup the HID objects
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)
consumer_control = ConsumerControl(usb_hid.devices)

# Setup the display
displayio.release_displays()
spi = busio.SPI(board.SCK, board.MOSI)
display_bus = displayio.FourWire(
    spi,
    command=board.OLED_DC,
    chip_select=board.OLED_CS,
    reset=board.OLED_RESET,
    baudrate=1000000,
)
display = SH1106(display_bus, width=OLED_WIDTH, height=OLED_HEIGHT)

# setup the keypad
key_pins = (
    board.KEY1,
    board.KEY2,
    board.KEY3,
    board.KEY4,
    board.KEY5,
    board.KEY6,
    board.KEY7,
    board.KEY8,
    board.KEY9,
    board.KEY10,
    board.KEY11,
    board.KEY12,
)
keys = keypad.Keys(key_pins, value_when_pressed=False, pull=True)

# setup the rotary encoder
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)
encoder = rotaryio.IncrementalEncoder(board.ROTB, board.ROTA)
encoder.position = 1
last_position = 1

# setup the neopixels
pixels = neopixel.NeoPixel(
    board.NEOPIXEL,
    PIXEL_NUM,
    brightness=PIXEL_BRIGHTNESS,
    auto_write=False,
    pixel_order=PIXEL_ORDER,
)


def update_text():
    # Updates the display text from key_maps
    text_area.text = key_maps[key_maps_index]["Name"]
    # Iterate through the variables and descriptions. i.e. text_area1, text_area2, etc
    for i in range(1, 12):
        globals()[f"text_area{i}"].text = key_maps[key_maps_index][i - 1][1][0:6]


def colorwheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if PIXEL_ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(j):
    for i in range(PIXEL_NUM):
        pixel_index = (i * 256 // PIXEL_NUM) + j
        pixels[i] = colorwheel(pixel_index & 255)
        pixels.show()


# Create display group
key_visual = displayio.Group(max_size=10)
display.show(key_visual)

# Draw an outer rectangle
color_bitmap = displayio.Bitmap(OLED_WIDTH, OLED_HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
key_visual.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(
    OLED_WIDTH - OLED_BORDER * 2 - 2, OLED_HEIGHT - OLED_BORDER * 2, 1
)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=OLED_BORDER + 2, y=OLED_BORDER
)
key_visual.append(inner_sprite)

# create the title text
text_area = label.Label(
    terminalio.FONT, text=" " * 6, color=0xFFFFFF, x=OLED_WIDTH // 2 - 10, y=10
)
key_visual.append(text_area)

# create the text area to hold key descriptions
i = 1
for y in [20, 30, 40, 50]:
    for x in [10, 50, 90]:
        globals()[f"text_area{i}"] = label.Label(
            terminalio.FONT, text=" " * 6, color=0xFFFFFF, x=x, y=y
        )
        key_visual.append(globals()[f"text_area{i}"])
        i += 1

# set the keymap to the first entry and update the text
key_maps_index = 1
update_text()

while True:
    # The key switch processing needs to been inside the RGB color cycle to prevent
    # keys pressed from being delayed until the complete color cycle is finished.
    for j in range(255):
        rainbow_cycle(j)

        event = keys.events.get()
        if event:
            if event.pressed:
                # lookup key macro
                map = key_maps[key_maps_index][event.key_number][0]
                # if string, write.  if dictionary press all together
                if isinstance(map, str):
                    try:
                        keyboard_layout.write(map)
                    except OSError:
                        microcontroller.reset()
                elif isinstance(map, list):
                    for key in map:
                        keyboard.press(key)
                    keyboard.release_all()
                else:
                    keyboard.send(map)

        # check if rotary encoder has moved.  If the rotary encoder was not pushed down, change the volume
        if encoder.position < last_position and button.value == True:
            last_position = encoder.position
            consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
        elif encoder.position > last_position and button.value == True:
            last_position = encoder.position
            consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)

        if encoder.position < last_position and button.value == False:
            # encoder was pushed before rotation.  Change keymap, not volume
            last_position = encoder.position
            key_maps_index -= 1
            if key_maps_index < 1:
                key_maps_index = len(key_maps)
            update_text()

        if encoder.position > last_position and button.value == False:
            last_position = encoder.position
            key_maps_index += 1
            if key_maps_index > len(key_maps):
                key_maps_index = 1
            update_text()
