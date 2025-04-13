
from machine import Pin, PWM  # type: ignore

from modules.utils import limit_value, map_value


class Motor:
    def __init__(self, forward_pin:int, backward_pin:int, PWM_LIMIT:tuple=(0, 1023)):
        """
        初始化电机对象
        @param speed_pin: 电机速度控制引脚
        @param dir_pin: 电机方向控制引脚
        @param PWM_LIMIT: PWM输出的上下限，默认为(0, 1023)
        """
        # 初始化电机控制对象
        self.PWM_LIMIT = PWM_LIMIT
        self.fw_speed = PWM(Pin(forward_pin), freq=500, duty=0)   # 速度控制引脚
        self.bk_speed = PWM(Pin(backward_pin), freq=500, duty=0)   # 速度控制引脚


    def set_speed(self, rate):
        """
        设置电机的速度
        @param rate: 速度百分比，范围[-100, 100]
        """
        pwm_value = int(map_value(abs(rate), (0, 100), self.PWM_LIMIT))
        pwm_value = limit_value(pwm_value, *self.PWM_LIMIT)  # 限制值

        # print(f"rate:{rate} pwm_value:{pwm_value}")

        if rate > 0:
            self.fw_speed.duty(pwm_value) 
            self.bk_speed.duty(0)

        elif rate < 0:
            self.fw_speed.duty(0)         
            self.bk_speed.duty(pwm_value)  

        else:
            self.fw_speed.duty(0)  
            self.bk_speed.duty(0) 


if __name__ == "__main__":
    import time

    pins = [1, 2, 14, 13, 38, 36, 8, 10]

    motor_lf = motor(pins[0], pins[1])  # 左前
    motor_rf = motor(pins[2], pins[3])  # 左后
    motor_rb = motor(pins[4], pins[5])  # 右前
    motor_lb = motor(pins[6], pins[7])  # 右后
    
    print("start")

    motor_lf.set_speed(50)
    print("lf test")
    time.sleep(2)

    motor_rf.set_speed(50)
    print("lb test")
    time.sleep(2)
    
    motor_rb.set_speed(50)
    print("rf test")
    time.sleep(2)
    
    motor_lb.set_speed(50)
    print("rb test")
    time.sleep(2)

    print("stop")
    motor_lf.set_speed(0)

    motor_lb.set_speed(0)
    
    motor_rf.set_speed(0)
    
    motor_rb.set_speed(0)
    

