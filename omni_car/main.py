
import time
from machine import Pin #导入Pin模块

import modules.now_recv as now

from modules.motion import RobotChassis
from modules.utils import TimeDiff, map_value, limit_value

time.sleep(2)  # 防止上电停不下来程序

LED=Pin(15,Pin.OUT) #构建led对象，GPIO46,输出
LED.value(1) #点亮LED，也可以使用led.on()

motor_pins = [1, 2, 14, 13, 38, 36, 8, 10]
robot = RobotChassis(motor_pins)


while True:
        data = now.read_espnow()

        if data:
            print(data)
            if data[0] == 1:
                if data[1] == 0 and data[2] == 0 and data[3] == 0 and data[4] == 0:
                    robot.stop()
                else:
                    robot.move(data[1], data[2], data[3])

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
