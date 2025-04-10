
import time
import math
import math

from machine import Pin, SPI

from lib.icm42688 import ICM42688P

import modules.fusion as fusion
from modules.utils import TimeDiff
from modules.filter import MovingAverageFilter

imu_dt = TimeDiff()

spi = SPI(1, sck=Pin(3), mosi=Pin(5), miso=Pin(7))
imu = ICM42688P(spi, cs_pin=9)
imu.initialize()


fuse = fusion.Fusion()
mva_filter = MovingAverageFilter(100)

# 初始化yaw角
yaw = 0.0

DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi

def normalize_angle(angle):
    """将角度调整到[-180, 180]范围内"""
    return (angle + 180) % 360 - 180

def imu_update():

    # 计算时间差
    # dt = imu_dt.time_diff() / 1_000_000_000  # 将ns转换为s
    # Hz = int(1/dt) if dt > 0.0001 else 0  # 避免第一次的数很大
    # print(f"{dt=:.3f}, {Hz=}")

    ax, ay, az = imu.read_accelerometer()
    gx, gy, gz = imu.read_gyroscope()
    # temp = imu.read_temperature()

    print(f"raw: {ax=:.2f}, {ay=:.2f}, {az=:.2f}, {gx=:.2f}, {gy=:.2f}, {gz=:.2f}")
    
    # gz += 0.804612  # 零偏

    # gz_err = gz - last_gz
    # gz_err_avg = mva_filter.filter(gz_err) # 计算零偏
    # times += 1

    #yaw += gz * dt  # 对陀螺仪的z轴数据进行积分以计算yaw角
    # print(f"Yaw Angle: {yaw} , dt: {dt:.6f}, Hz: {int(1/dt)}")

    # 计算 pitch 和 roll
    #pitch = math.atan2(ax, math.sqrt(ay**2 + az**2)) * RAD2DEG
    #roll  = math.atan2(ay, math.sqrt(ax**2 + az**2)) * RAD2DEG

    # 打印
    #print(f"raw: {yaw=:.2f}, {pitch=:.2f}, {roll=:.2f}, {gz_err_avg=:.6f}, {times}")

    # 更新融合数据
    fuse.update_nomag((ax, ay, az), (gx, gy, gz))

    fuse.roll = normalize_angle(fuse.roll-180)

    # print(f"fuse: {fuse.heading:.2f}, {fuse.pitch:.2f}, {(fuse.roll):.2f}, {dt=:.3f}, {Hz=}")

    return fuse.heading, fuse.pitch, fuse.roll, (gx, gy, gz)


if __name__ == "__main__":

    led = Pin(15, Pin.OUT)
    led.value(1)

    while True:

        yaw, roll, pitch, _ = imu_update()  # 注意, pitch 和 roll 互换位置
        
        roll = -roll
 
        print(f"{yaw=:.2f}, {pitch=:.2f}, {roll=:.2f}")

        time.sleep(0.1)
        led.value(not led.value())   