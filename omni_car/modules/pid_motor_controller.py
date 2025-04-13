# 
from machine import Timer

from modules.encoder import Encoder
from modules.motor import Motor
from modules.pid import PID

class Encoders:
    def __init__(self, pins:list, period:float=0.01):
        self.encoder_lf = Encoder(pins[0], pins[1], dt=period)
        self.encoder_rf = Encoder(pins[2], pins[3], dt=period)
        self.encoder_rb = Encoder(pins[4], pins[5], dt=period)
        self.encoder_lb = Encoder(pins[6], pins[7], dt=period)

        self.pos = [0, 0, 0, 0]
        self.speed = [0, 0, 0, 0]  # 单位: 脉冲/采样周期
        self.odometry = [0, 0, 0]  # 前进速度, 侧向速度, 角速度

        self.period = period  # 设置速度更新周期
        
        tim = Timer(1)
        tim.init(period=int(self.period*1000), mode=Timer.PERIODIC,callback=self.update_speed)  # 每个周期 计算一次速度


    def update_speed(self, timer_callback):
        # 计算速度
        self.encoder_lf.update_speed()
        self.encoder_rf.update_speed()
        self.encoder_rb.update_speed()
        self.encoder_lb.update_speed()
        
        self.speed[0] = self.encoder_lf.speed
        self.speed[1] = self.encoder_rf.speed
        self.speed[2] = self.encoder_rb.speed
        self.speed[3] = self.encoder_lb.speed


        self.pos[0] = self.encoder_lf.position()
        self.pos[1] = self.encoder_rf.position()
        self.pos[2] = self.encoder_rb.position()
        self.pos[3] = self.encoder_lb.position()
        # print(f"pos: {self.pos}, rate: {self.speed}")

        # 计算速度对应的里程计增量
        odom_increment = self.odometer(*self.speed)

        # 逐个元素累加
        self.odometry[0] += odom_increment[0]
        self.odometry[1] += odom_increment[1]
        self.odometry[2] += odom_increment[2]

    def odometer(self, v_lf, v_rf, v_rb, v_lb) -> list: 
        v_x = (v_lf + v_rf - v_rb - v_lb) / 2.0
        v_y = (v_lf - v_rf + v_rb - v_lb) / 2.0
        v_w = (-v_lf + v_rf + v_rb - v_lb) / 2.0
        return v_x, v_y, v_w

    
    def get_odometry(self) -> list:
        return self.odometry
    
    def get_speed(self) -> list:
        return self.speed
    
    def get_pos(self) -> list:
        return self.pos


class Motors:
    def __init__(self, pins:list):
        if len(pins) != 8:
            raise ValueError("Expected 8 pin values for 4 motors.")

        self.motor_lf = Motor(pins[0], pins[1])  # 左前
        self.motor_rf = Motor(pins[2], pins[3])  # 左后
        self.motor_rb = Motor(pins[4], pins[5])  # 右前
        self.motor_lb = Motor(pins[6], pins[7])  # 右后

    def set_speed(self, speed:list):
        self.motor_lf.set_speed(speed)
        self.motor_rf.set_speed(speed)
        self.motor_rb.set_speed(speed)
        self.motor_lb.set_speed(speed)    
    
    # 预留直接电机控制的方法
    def set_speed_lf(self, speed):
        self.motor_lf.set_speed(speed)
    
    def set_speed_rf(self, speed):
        self.motor_rf.set_speed(speed)
    
    def set_speed_rb(self, speed):
        self.motor_rb.set_speed(speed)
    
    def set_speed_lb(self, speed):
        self.motor_lb.set_speed(speed)


if __name__ == "__main__":

    import time

    encoder_pins = [4, 6, 39, 40, 21, 34, 12, 11]
    encoders = Encoders(encoder_pins)

    for i in range(10000):
        print(f"pos: {encoders.pos}, rate: {encoders.speed}, odometry: {encoders.odometry}")
        time.sleep(0.01)

    motor_pins = [1, 2, 14, 13, 38, 36, 8, 10]
    motors = Motors(motor_pins)

    # motors.set_speed(50)
    # time.sleep(2)
    # motors.set_speed(-20)
    # time.sleep(2)
    # motors.set_speed(0)
    # time.sleep(1)

    time.sleep(1)

    # pid_speed_lf = PID(kp=0.3, ki=0.0, kd=0.02, setpoint=0, output_limits=(-1023, 1023))

    # while True:
        
    #     pid_speed_lf.set_point(13*20*2)
        
    #     for i in range(250):
    #         encoder_lf = encoders.get_pos()[3]
    #         pwm_lf = pid_speed_lf.update(encoder_lf)
    #         motors.set_speed_lb(pwm_lf)

    #         print(f"target: {pid_speed_lf.setpoint}, encoder: {encoder_lf}, pwm: {pwm_lf}")
            
    #         time.sleep(0.01)
            

    #     pid_speed_lf.set_point(0)
        
    #     for i in range(250):
    #         encoder_lf = encoders.get_pos()[3]
    #         pwm_lf = pid_speed_lf.update(encoder_lf)
    #         motors.set_speed_lb(pwm_lf)

    #         print(f"target: {pid_speed_lf.setpoint}, encoder: {encoder_lf}, pwm: {pwm_lf}")
            
    #         time.sleep(0.01)
            
        
