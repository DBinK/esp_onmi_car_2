
import re
import time
import json
import struct

import espnow
import network
from machine import Pin

from modules.utils import map_value


# 初始化 WiFi 和 espnow
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()  # 因为 ESP8266 会自动连接到最后一个接入点

now = espnow.ESPNow()
now.active(True)  # 连接dk广播地址
now.add_peer(b"\xff\xff\xff\xff\xff\xff")


# 初始化 LED
led = Pin(15, Pin.OUT, value=1)


DEAD_AREA = 20  # 摇杆死区
MAP_COEFF = 58  # 摇杆映射系数 (根据实际需求调整)

OFFSET_lx = 16  # 摇杆校准偏移值
OFFSET_ly = 35
OFFSET_rx = 6
OFFSET_ry = 16


def read_espnow():
    """读取espnow数据并进行解包处理"""
    host, msg = now.recv(0)  # 读取所有可用的数据, 参数: 超时时间ms

    #print("espnow数据:", msg)

    if msg:  # 如果没有数据，则返回
        
        msg_str = msg.decode('utf-8')  # msg 解码为字符串
        data = json.loads(msg_str)     # 处理接收到的数据

        data[1] += OFFSET_lx   # lx 摇杆校准
        data[2] += OFFSET_ly   # ly 摇杆校准
        data[3] += OFFSET_rx   # rx 摇杆校准
        data[4] += OFFSET_ry   # ry 摇杆校准

        # print(f"矫正后数据: lx={data[1]}, ly={data[2]}, rx={data[3]}, ry={data[4]}")

        # 检查任意摇杆是否在活动状态
        stick_work = any(abs(value - 127) > DEAD_AREA for value in data[1:5])  

        if stick_work or data[5] != 0x8 or data[6] != 0x0:  # 如果任意摇杆或按键在活动状态，则闪烁led
            led.value(not led.value())  # 闪烁led
        else:  
            led.value(0)   # 如果所有摇杆和按键都不在活动状态，则关闭led

        return data, stick_work
    
    else:  # 如果没有数据，则返回
        return None, False

def process_data(data):
    
    data, stick_work = read_espnow()

    if data:
        
        if data[6] != 0x0:
            # 电机停转
            pass

        if stick_work:

            ly = data[1]
            lx = data[2]
            ry = data[4]
            rx = data[3]
            
            # 底盘控制
            _ly = map_value(ly, (0, 255), (-127, 127))  
            _lx = map_value(lx, (0, 255), (-127, 127))  
            _ry = map_value(ry, (0, 255), (-127, 127))  
            _rx = map_value(rx, (0, 255), (-127, 127))

            print(f"摇杆映射后数据: lx={_lx}, ly={_ly}, rx={_rx}, ry={_ry}")

            data[1] = _ly
            data[2] = _lx
            data[3] = _rx
            data[4] = _ry
            
            # print(f"摇杆缩放后数据: lx={_lx}, ly={_ly}, rx={_rx}, ry={_ry}")

            return data


if __name__ == "__main__":
    print("正在读取espnow数据...")
    while True:
        data = read_espnow()

        if data:
            print(data)

        time.sleep(0.1)


    # GamePad 数据格式

    gamepad_data = {
        "id": 0x01,  # 手柄 ID

        "lx": 0,  # 左摇杆X轴 0x00 ~ 0xFF (0~255)
        "ly": 0,  # 左摇杆Y轴 0x00 ~ 0xFF (0~255)
        "rx": 0,  # 右摇杆X轴 0x00 ~ 0xFF (0~255)
        "ry": 0,  # 右摇杆Y轴 0x00 ~ 0xFF (0~255)

        "abxy & dpad": 0,  
        "ls & rs & start & back": 0,

        "mode": 0x06,  # 预留模式位
    }