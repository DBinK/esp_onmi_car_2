# imu_filters.py
# 该文件包含常用的IMU滤波器，封装为类，适用于MicroPython环境。
# 包含低通滤波器、高通滤波器、互补滤波器和卡尔曼滤波器。

import array
import math

# 低通滤波器 (Low Pass Filter)
# 用于去除高频噪声，保留低频信号。
class LowPassFilter:
    def __init__(self, alpha):
        """
        初始化低通滤波器。
        :param alpha: 滤波系数，范围 [0, 1]。值越小，滤波效果越强。
        """
        self.alpha = alpha
        self.filtered_value = array.array('f', [0.0, 0.0, 0.0])  # 使用array加速，存储滤波后的值

    def update(self, new_value):
        """
        更新滤波器状态。
        :param new_value: 新的输入值，格式为 array.array('f', [x, y, z])。
        :return: 滤波后的值，格式为 array.array('f', [x, y, z])。
        """
        for i in range(3):
            self.filtered_value[i] = self.alpha * new_value[i] + (1 - self.alpha) * self.filtered_value[i]
        return self.filtered_value


# 高通滤波器 (High Pass Filter)
# 用于去除低频噪声，保留高频信号。
class HighPassFilter:
    def __init__(self, alpha):
        """
        初始化高通滤波器。
        :param alpha: 滤波系数，范围 [0, 1]。值越大，滤波效果越强。
        """
        self.alpha = alpha
        self.filtered_value = array.array('f', [0.0, 0.0, 0.0])  # 存储滤波后的值
        self.last_raw_value = array.array('f', [0.0, 0.0, 0.0])  # 存储上一次的原始值

    def update(self, new_value):
        """
        更新滤波器状态。
        :param new_value: 新的输入值，格式为 array.array('f', [x, y, z])。
        :return: 滤波后的值，格式为 array.array('f', [x, y, z])。
        """
        for i in range(3):
            self.filtered_value[i] = self.alpha * (self.filtered_value[i] + new_value[i] - self.last_raw_value[i])
            self.last_raw_value[i] = new_value[i]
        return self.filtered_value


# 互补滤波器 (Complementary Filter)
# 结合加速度计和陀螺仪的数据，适用于姿态估计。
class ComplementaryFilter:
    def __init__(self, alpha):
        """
        初始化互补滤波器。
        :param alpha: 滤波系数，范围 [0, 1]。值越大，陀螺仪数据权重越高。
        """
        self.alpha = alpha
        self.angle = array.array('f', [0.0, 0.0, 0.0])  # 存储估计的角度

    def update(self, accel_data, gyro_data, dt):
        """
        更新滤波器状态。
        :param accel_data: 加速度计数据，格式为 array.array('f', [x, y, z])。
        :param gyro_data: 陀螺仪数据，格式为 array.array('f', [x, y, z])。
        :param dt: 时间间隔（秒）。
        :return: 估计的角度，格式为 array.array('f', [x, y, z])。
        """
        for i in range(3):
            # 使用加速度计数据计算角度
            accel_angle = math.atan2(accel_data[i], math.sqrt(accel_data[(i + 1) % 3] ** 2 + accel_data[(i + 2) % 3] ** 2))
            # 结合陀螺仪数据进行滤波
            self.angle[i] = self.alpha * (self.angle[i] + gyro_data[i] * dt) + (1 - self.alpha) * accel_angle
        return self.angle


class MovingAverageFilter:
    """
    递推平均滤波器（滑动窗口），维持一个固定长度的数据队列，每次加入新数据时移除最早的数据。
    
    参数:
        size: int, 滤波窗口大小，默认为10。
    """
    def __init__(self, size=10):
        """ 初始化MovingAverage对象。"""
        self.size = size
        self.buffer = [0] * size
        self.index = 0
        self.total = 0

    def filter(self, value, size=None):
        """
        更新缓冲区并计算新的移动平均值。
        
        参数:
        value (float): 新的输入值。
        
        返回:
        float: 当前所有缓冲区中值的移动平均值。
        
        该方法首先从当前总和中减去缓冲区中即将被替换的值，然后将新的输入值存储在缓冲区中，
        接着更新总和并调整索引以准备下一次输入值的存储位置。最后返回当前的移动平均值。
        """
        if size is not None:
            self.size = size
            
        self.total -= self.buffer[self.index]
        self.buffer[self.index] = value
        self.total += value
        self.index = (self.index + 1) % self.size
        return self.total / self.size


class ZeroOffsetCalculator:
    def __init__(self, filter_func):
        self.last_value = [0]
        self.filter = filter_func

    def cal_zero_offset(self, value):
        if self.last_value[0] != 0:
            value_err = value - self.last_value[0]
        else:
            value_err = 0

        self.last_value[0] = value

        value_err_avg = self.filter(value_err)

        return value_err_avg

        
if __name__ == "__main__":

    pass