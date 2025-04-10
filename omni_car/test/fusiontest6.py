# fusiontest6.py Simple test program for 6DOF sensor fusion on Pyboard
# Author Peter Hinch
# Released under the MIT License (MIT)
# Copyright (c) 2017 Peter Hinch
# V0.8 14th May 2017 Option for external switch for cal test. Make platform independent.
# V0.7 25th June 2015 Adapted for new MPU9x50 interface

import time

from machine import Pin, SPI

from modules.fusion import Fusion
from lib.icm42688 import ICM42688P


spi = SPI(1, sck=Pin(3), mosi=Pin(5), miso=Pin(7))

cs_pin = 9  # 替换为实际的CS引脚编号

imu = ICM42688P(spi, cs_pin)
imu.initialize()

fuse = Fusion()

# Choose test to run
Timing = True

if Timing:
    accel = imu.read_accelerometer()
    gyro = imu.read_gyroscope()
    start = time.ticks_us()  # Measure computation time only
    fuse.update_nomag(accel, gyro) # 979μs on Pyboard
    t = time.ticks_diff(time.ticks_us(), start)
    print("Update time (uS):", t)

count = 0

while True:
    #fuse.update_nomag(imu.read_accelerometer(), imu.read_gyroscope())
    fuse.update(imu.read_accelerometer(), imu.read_gyroscope())
    if count % 1 == 0:
        print("Heading, Pitch, Roll: {:7.3f} {:7.3f} {:7.3f}".format(fuse.heading, fuse.pitch, fuse.roll))
    time.sleep_ms(20)
    count += 1

