# encoder_portable.py

# Encoder Support: this version should be portable between MicroPython platforms
# Thanks to Evan Widloski for the adaptation to use the machine module

# Copyright (c) 2017-2022 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

from machine import Pin # type: ignore

class Encoder:
    """ 
    Encoder class for MicroPython.
    @param pin_x: Pin number for X channel
    @param pin_y: Pin number for Y channel
    @param dt: Period of update in seconds. Default 0.001 (1ms)
    @param scale: Scale factor for position. Default 1.
    """
    def __init__(self, pin_x: int, pin_y: int, dt: float = 0.01, scale: float = 1):
        self.scale = scale
        self.forward = True
        self.pin_x = Pin(pin_x, Pin.IN, Pin.PULL_UP)
        self.pin_y = Pin(pin_y, Pin.IN, Pin.PULL_UP)
        self._x = self.pin_x.value()
        self._y = self.pin_y.value()
        self._pos = 0
        self._prev_pos = 0
        self.speed = 0
        self.dt = dt   
        try:
            self.x_interrupt = self.pin_x.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.x_callback, hard=True)
            self.y_interrupt = self.pin_y.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.y_callback, hard=True)
        except TypeError:
            self.x_interrupt = self.pin_x.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.x_callback)
            self.y_interrupt = self.pin_y.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.y_callback)

    def x_callback(self, pin_x):
        if (x := pin_x.value()) != self._x:  # Reject short pulses
            self._x = x
            self.forward = x ^ self.pin_y.value()
            self._pos += 1 if self.forward else -1

    def y_callback(self, pin_y):
        if (y := pin_y.value()) != self._y:
            self._y = y
            self.forward = y ^ self.pin_x.value() ^ 1
            self._pos += 1 if self.forward else -1

    def position(self, value=None):
        if value is not None:
            self._pos = round(value / self.scale)  # Improvement provided by @IhorNehrutsa
        return self._pos * self.scale

    def value(self, value=None):
        if value is not None:
            self._pos = value
        return self._pos
    
    def update_speed(self):  # pulse/sec
        self.speed = (self._pos - self._prev_pos) / self.dt
        self._prev_pos = self._pos
    
    def reset(self):
        self._pos = 0
        self._prev_pos = 0


if __name__ == '__main__':

    from machine import Pin
    import time

#     AH1 = Pin(4, Pin.IN, Pin.PULL_UP)
#     AH2 = Pin(6, Pin.IN, Pin.PULL_UP)

    encoder = Encoder(4, 6)

    while True:
        print(f"pos: {encoder.position()}")
        time.sleep(0.1)