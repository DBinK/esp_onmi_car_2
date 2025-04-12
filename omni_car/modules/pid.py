import time

class PID:
    def __init__(self, kp=1, ki=0, kd=0, setpoint=0, output_limits=(None, None), mode='position'):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0
        self.output_limits = output_limits
        self.last_time = time.time_ns()  # 使用ns计时
        self.prev_output = 0  # 新增变量，存储上一次的控制输出
        self.mode = mode  # 新增变量，存储控制器模式

    def update(self, measured_value, setpoint=None, derivative=None):
        current_time = time.time_ns()
        dt = (current_time - self.last_time) / 1_000_000_000  # 转换为秒

        if setpoint is not None:
            self.setpoint = setpoint

        error = self.setpoint - measured_value
        self.integral += error * dt

        if derivative is None:
            derivative = (error - self.prev_error) / dt if dt > 0 else 0

        if self.mode == 'position':    # 位置式PID
            output = self.kp * error + self.ki * self.integral + self.kd * derivative

        elif self.mode == 'incremental':    # 增量式PID
            delta_output = self.kp * (error - self.prev_error) + self.ki * error * dt + self.kd * derivative
            output = self.prev_output + delta_output
            
        else:
            raise ValueError("Mode must be 'position' or 'incremental'")

        # 应用输出限制
        if self.output_limits[0] is not None and output < self.output_limits[0]:
            output = self.output_limits[0]
        if self.output_limits[1] is not None and output > self.output_limits[1]:
            output = self.output_limits[1]

        # 更新上一次的控制输出
        self.prev_output = output

        self.prev_error = error
        self.last_time = current_time
        return output

# 示例使用
if __name__ == "__main__":
    pid = PID(1.0, 1.0, 0.0, setpoint=10.0, output_limits=(-10, 10), mode='position')
    measured_value = 0.0

    for i in range(1000):
        control = pid.update(measured_value)
        measured_value += control * 0.1
        print(f"当前步数:{i}, 控制输出: {control}, 当前值: {measured_value}")
        time.sleep(0.01)  # 模拟控制循环的时间间隔
        
    pid.setpoint = 20
    
    for i in range(1000):
        control = pid.update(measured_value)
        measured_value += control * 0.1
        print(f"当前步数:{i}, 控制输出: {control}, 当前值: {measured_value}")
        time.sleep(0.01)  # 模拟控制循环的时间间隔

    # 切换到增量式模式
    pid.mode = 'incremental'
    measured_value = 0.0

    for i in range(1000):
        control = pid.update(measured_value)
        measured_value += control * 0.1
        print(f"当前步数:{i}, 控制输出: {control}, 当前值: {measured_value}")
        time.sleep(0.01)  # 模拟控制循环的时间间隔