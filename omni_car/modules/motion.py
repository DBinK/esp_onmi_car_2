from omni_car.modules.motor import motor

class RobotChassis():
    def __init__(self, pins):
        """
        初始化机器人控制器，并设置电机的引脚。
        
        参数:
        pins (list): 包含四个电机的8个引脚列表，顺序为左前、左后、右前、右后。
        
        示例:
        controller = RobotController([0, 1, 2, 3, 4, 5, 6, 7])
        """
        # 检查引脚列表的长度是否为4
        if len(pins) != 8:
            raise ValueError("Expected 8 pin values for 4 motors.")
        
        self.motor_lf = motor(pins[0], pins[1])  # 左前
        self.motor_rf = motor(pins[2], pins[3])  # 左后
        self.motor_rb = motor(pins[4], pins[5])  # 右前
        self.motor_lb = motor(pins[6], pins[7])  # 右后
    
    def scale_speed(self, v1, v2, v3, v4):
        """
        限制速度，确保每个输入电机的速度值不超过100%, 且保证运动学解算结果准确
        """
        max_speed = 100  # 检查是否有速度超过最大值
        
        if abs(v1) > max_speed or abs(v2) > max_speed or abs(v3) > max_speed or abs(v4) > max_speed:
            
            max_current_speed = max(abs(v1), abs(v2), abs(v3), abs(v4))  # 计算当前速度的最大绝对值
            scale = max_speed / max_current_speed  # 计算缩放因子
            v1 *= scale  
            v2 *= scale
            v3 *= scale
            v4 *= scale
            
        return v1, v2, v3, v4  # 返回处理后的速度值

    def move(self, v_x, v_y, v_w): 
        """ 输入期望运动状态, 输出电机所需的运动速度 """

        # 运动学解算 
        v_lf = v_x + v_y - v_w  # 左前
        v_rf = v_x - v_y + v_w  # 右前
        v_rb = -v_x - v_y - v_w  # 右后
        v_lb = -v_x + v_y + v_w  # 左后

        # 缩放速度, 保证运动学解算准确
        v_lf, v_rf, v_lb, v_rb = self.scale_speed(v_lf, v_rf, v_lb, v_rb)

        # 设置电机速度
        self.motor_lf.set_speed(v_lf)
        self.motor_rf.set_speed(v_rf)
        self.motor_lb.set_speed(v_lb)
        self.motor_rb.set_speed(v_rb)

    # 封装一些简单运动的控制方法
    def go_forward(self, rate):
        self.move(rate, 0, 0)

    def go_backward(self, rate):
        self.move(-rate, 0, 0)

    def go_left(self, rate):
        self.move(0, -rate, 0)

    def go_right(self, rate):
        self.move(0, rate, 0)

    def turn_left(self, rate):
        self.move(0, 0, rate)

    def turn_right(self, rate):
        self.move(0, 0, -rate)

    def stop(self):
        self.move(0, 0, 0)

    # 预留直接电机控制的方法
    def motor_lf_test(self, rate):
        self.motor_lf.set_speed(rate)

    def motor_lb_test(self, rate):
        self.motor_lb.set_speed(rate)

    def motor_rf_test(self, rate):
        self.motor_rf.set_speed(rate)

    def motor_rb_test(self, rate):
        self.motor_rb.set_speed(rate)

if __name__ == "__main__":
    import time
    motor_pins = [1, 2, 14, 13, 38, 36, 8, 10]
    robot = RobotChassis(motor_pins)

    while True:
        robot.turn_left(30)
        time.sleep(3)

        robot.turn_right(30)
        time.sleep(3)
        
        robot.go_forward(30)
        time.sleep(3)

        robot.go_backward(30)
        time.sleep(3)

        robot.go_left(30)
        time.sleep(3)

        robot.go_right(30)
        time.sleep(3)

        
        
        
        
        