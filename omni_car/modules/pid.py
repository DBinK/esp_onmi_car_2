import time

class PID:
    def __init__(self, kp=1, ki=0, kd=0, setpoint=0, output_limits=(None, None)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0
        self.output_limits = output_limits
        self.last_time = time.time_ns()  # 使用ns计时

    def update(self, measured_value, setpoint=None, derivative=None):
        current_time = time.time_ns()
        dt = (current_time - self.last_time) / 1_000_000_000  # 转换为秒

        if setpoint is not None:
            self.setpoint = setpoint

        error = self.setpoint - measured_value
        self.integral += error * dt

        if derivative is None:
            derivative = (error - self.prev_error) / dt if dt > 0 else 0
            
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        if self.output_limits[0] is not None and output < self.output_limits[0]:
            output = self.output_limits[0]
        if self.output_limits[1] is not None and output > self.output_limits[1]:
            output = self.output_limits[1]

        self.prev_error = error
        self.last_time = current_time
        return output
    
    # def update_with_det(self, measured_value, derivative, setpoint=None):
    #     current_time = time.time_ns()
    #     dt = (current_time - self.last_time) / 1_000_000_000  # 转换为秒

    #     if setpoint is not None:
    #         self.setpoint = setpoint

    #     error = self.setpoint - measured_value
    #     self.integral += error * dt
    #     #derivative = (error - self.prev_error) / dt if dt > 0 else 0
        
    #     output = self.kp * error + self.ki * self.integral + self.kd * derivative  # 使用给定的微分值
        
    #     if self.output_limits[0] is not None and output < self.output_limits[0]:
    #         output = self.output_limits[0]
    #     if self.output_limits[1] is not None and output > self.output_limits[1]:
    #         output = self.output_limits[1]

    #     self.prev_error = error
    #     self.last_time = current_time
    #     return output

# 示例使用
if __name__ == "__main__":
    pid = PID(1.0, 1.0, 0.0, setpoint=10.0, output_limits=(-10, 10))
    measured_value = 0.0

    for i in range(100):
        control = pid.update(measured_value)
        measured_value += control * 0.1
        print(f"当前步数:{i*0.001}, 控制输出: {control}, 当前值: {measured_value}")
        time.sleep(0.01)  # 模拟控制循环的时间间隔
        
    pid.setpoint = 20
    
    for i in range(100):
        control = pid.update(measured_value)
        measured_value += control * 0.1
        print(f"当前步数:{i*0.001}, 控制输出: {control}, 当前值: {measured_value}")
        time.sleep(0.01)  # 模拟控制循环的时间间隔   