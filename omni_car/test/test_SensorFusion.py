# fusiontest6.py Simple test program for 6DOF sensor fusion on Pyboard
# Author Peter Hinch
# Released under the MIT License (MIT)
# Copyright (c) 2017 Peter Hinch
# V0.8 14th May 2017 Option for external switch for cal test. Make platform independent.
# V0.7 25th June 2015 Adapted for new MPU9x50 interface

import time

from machine import Pin, SPI

from modules.SensorFusion import SensorFusion
from modules.deltat import DeltaT
from lib.icm42688 import ICM42688P


# 示例用法
if __name__ == "__main__":
    
    spi = SPI(1, sck=Pin(3), mosi=Pin(5), miso=Pin(7))
    
    cs_pin = 9  # 替换为实际的CS引脚编号
    
    imu = ICM42688P(spi, cs_pin)
    imu.initialize()

    sf = SensorFusion()
    
    delta_t = DeltaT(None)

    led = Pin(15, Pin.OUT)
    led.value(1)

    while True: 
        
        gx, gy, gz = imu.read_gyroscope()  # 陀螺仪数据
        ax, ay, az = imu.read_accelerometer()  # 加速度计数据

        #print(f"加速度: X={accel_x:.2f} G, Y={accel_y:.2f} G, Z={accel_z:.2f} G")
        #print(f"角速度: X={gyro_x:.2f} DPS, Y={gyro_y:.2f} DPS, Z={gyro_z:.2f} DPS")
        #print(f"温度: {temp:.2f} C")

        deltat = delta_t(None)

        sf.MahonyUpdateIMU(gx, gy, gz, ax, ay, az, 0.01)  # 使用陀螺仪和加速度计数据更新传感器融合    

        # 获取欧拉角
        roll = sf.getRoll()
        pitch = sf.getPitch()
        yaw = sf.getYaw()

        print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")

        time.sleep(0.01)

        led.value(not led.value())   

# if __name__ == '__main__':

#     # 示例：更新传感器数据
#     gx, gy, gz = 0.1, 0.2, 0.3  # 陀螺仪数据
#     ax, ay, az = 0.0, 0.0, 1.0  # 加速度计数据
#     mx, my, mz = 0.0, 0.0, 0.0  # 磁力计数据

#     # 更新传感器数据
#     deltat = 0.01  # 时间间隔

#     sf.MahonyUpdateIMU(gx, gy, gz, ax, ay, az, deltat)
#     #sf.MahonyUpdate(gx, gy, gz, ax, ay, az, mx, my, mz, deltat)

#     # 获取欧拉角
#     roll = sf.getRoll()
#     pitch = sf.getPitch()
#     yaw = sf.getYaw()

#     print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")