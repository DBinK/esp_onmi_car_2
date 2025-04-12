
import time
from machine import Pin #导入Pin模块

import modules.now_recv as now

from modules.motion import RobotChassis
from modules.utils import TimeDiff, map_value, limit_value

time.sleep(1)  # 防止上电停不下来程序

LED=Pin(15,Pin.OUT) #构建led对象，GPIO46,输出
LED.value(1) #点亮LED，也可以使用led.on()

motor_pins = [1, 2, 14, 13, 38, 36, 8, 10]
robot = RobotChassis(motor_pins)

scale_x = 0.8
scale_y = 0.8
scale_w = 0.4

while True:
    data = now.read_espnow()
    data = now.process_data(data)

    if data:
        print(data)
        if data[1] > 10 and data[2] > 10 and data[3] > 10 and data[4] > 10:
            robot.stop()
        else:
            robot.move(-data[1]*scale_x, data[2]*scale_y, -data[3]*scale_w)
    else:
        robot.stop()

    time.sleep(0.01)

    # robot.turn_left(40)
    # time.sleep(3)

    # robot.turn_right(40)
    # time.sleep(3)
    
    # robot.go_forward(40)
    # time.sleep(3)

    # robot.go_backward(40)
    # time.sleep(3)

    # robot.go_left(40)
    # time.sleep(3)

    # robot.go_right(40)
    # time.sleep(3)
