"""LCD on 01Studio pyController  240x240

https://pycontroller.01studio.cc/zh-cn/latest/about/about.html

"""

from machine import Pin, SPI
import st7789py as st7789

TFA = 0
BFA = 80
WIDE = 1
TALL = 0
SCROLL = 0  # orientation for scroll.py
FEATHERS = 1  # orientation for feathers.py


def config(rotation=0):
    """
    Configures and returns an instance of the ST7789 display driver.

    Args:
        rotation (int): The rotation of the display. Defaults to 0.

    Returns:
        ST7789: An instance of the ST7789 display driver.
    """

    return st7789.ST7789(
        SPI(
            2,
            baudrate=40_000_000,
            polarity=0,
            sck=Pin(40, Pin.OUT),
            mosi=Pin(41, Pin.OUT),
            miso=None,
        ),
        240,
        240,
        reset=Pin(42, Pin.OUT),
        cs=Pin(39, Pin.OUT),
        dc=Pin(38, Pin.OUT),
        # backlight=Pin(13, Pin.OUT),
        rotation=rotation,
    )


