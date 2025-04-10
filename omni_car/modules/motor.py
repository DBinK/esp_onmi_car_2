
from machine import Pin, PWM  # type: ignore

from modules.utils import limit_value, map_value


class AT8236:
    def __init__(self, forward_pin, backward_pin, PWM_LIMIT=(0, 1023)):
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
    pass