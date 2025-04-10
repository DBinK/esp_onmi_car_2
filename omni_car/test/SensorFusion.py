import math
import time
import struct

class SensorFusion:
    def __init__(self):
        # 初始化参数
        self.beta = 0.1  # Madgwick 算法参数
        self.twoKp = 2.0 * 0.5  # Mahony 算法参数
        self.twoKi = 2.0 * 0.0  # Mahony 算法参数

        # 四元数初始化
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0

        # 积分误差项
        self.integralFBx = 0.0
        self.integralFBy = 0.0
        self.integralFBz = 0.0

        # 角度计算标志
        self.anglesComputed = False
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

        # 时间相关变量
        self.lastUpdate = time.ticks_us()

    def invSqrt(self, x):
        """快速计算平方根的倒数（适用于 MicroPython）"""
        halfx = 0.5 * x
        y = x
        # 使用 struct 将浮点数转换为整数进行位操作
        packed_y = struct.pack('!f', y)
        i = struct.unpack('!I', packed_y)[0]
        i = 0x5f3759df - (i >> 1)
        packed_i = struct.pack('!I', i)
        y = struct.unpack('!f', packed_i)[0]
        y = y * (1.5 - (halfx * y * y))  # 一次牛顿迭代
        return y

    def computeAngles(self):
        """计算欧拉角"""
        self.roll = math.atan2(self.q0 * self.q1 + self.q2 * self.q3, 0.5 - self.q1 * self.q1 - self.q2 * self.q2)
        self.pitch = math.asin(-2.0 * (self.q1 * self.q3 - self.q0 * self.q2))
        self.yaw = math.atan2(self.q1 * self.q2 + self.q0 * self.q3, 0.5 - self.q2 * self.q2 - self.q3 * self.q3)
        self.anglesComputed = True

    def MahonyUpdate(self, gx, gy, gz, ax, ay, az, mx, my, mz, deltat):
        """Mahony AHRS 算法更新（使用磁力计）"""
        recipNorm = 0.0
        q0q0, q0q1, q0q2, q0q3, q1q1, q1q2, q1q3, q2q2, q2q3, q3q3 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        hx, hy, bx, bz = 0.0, 0.0, 0.0, 0.0
        halfvx, halfvy, halfvz, halfwx, halfwy, halfwz = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        halfex, halfey, halfez = 0.0, 0.0, 0.0
        qa, qb, qc = 0.0, 0.0, 0.0

        # 如果磁力计数据无效，使用 IMU 算法
        if mx == 0.0 and my == 0.0 and mz == 0.0:
            self.MahonyUpdateIMU(gx, gy, gz, ax, ay, az, deltat)
            return

        # 如果加速度计数据有效
        if not (ax == 0.0 and ay == 0.0 and az == 0.0):
            # 归一化加速度计数据
            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az)
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm

            # 归一化磁力计数据
            recipNorm = self.invSqrt(mx * mx + my * my + mz * mz)
            mx *= recipNorm
            my *= recipNorm
            mz *= recipNorm

            # 辅助变量
            q0q0 = self.q0 * self.q0
            q0q1 = self.q0 * self.q1
            q0q2 = self.q0 * self.q2
            q0q3 = self.q0 * self.q3
            q1q1 = self.q1 * self.q1
            q1q2 = self.q1 * self.q2
            q1q3 = self.q1 * self.q3
            q2q2 = self.q2 * self.q2
            q2q3 = self.q2 * self.q3
            q3q3 = self.q3 * self.q3

            # 地球磁场参考方向
            hx = 2.0 * (mx * (0.5 - q2q2 - q3q3) + my * (self.q1 * self.q2 - self.q0 * self.q3) + mz * (self.q1 * self.q3 + self.q0 * self.q2))
            hy = 2.0 * (mx * (self.q1 * self.q2 + self.q0 * self.q3) + my * (0.5 - q1q1 - q3q3) + mz * (self.q2 * self.q3 - self.q0 * self.q1))
            bx = math.sqrt(hx * hx + hy * hy)
            bz = 2.0 * (mx * (self.q1 * self.q3 - self.q0 * self.q2) + my * (self.q2 * self.q3 + self.q0 * self.q1) + mz * (0.5 - q1q1 - q2q2))

            # 估计重力和磁场方向
            halfvx = self.q1 * self.q3 - self.q0 * self.q2
            halfvy = self.q0 * self.q1 + self.q2 * self.q3
            halfvz = self.q0 * self.q0 - 0.5 + self.q3 * self.q3
            halfwx = bx * (0.5 - q2q2 - q3q3) + bz * (self.q1 * self.q3 - self.q0 * self.q2)
            halfwy = bx * (self.q1 * self.q2 - self.q0 * self.q3) + bz * (self.q0 * self.q1 + self.q2 * self.q3)
            halfwz = bx * (self.q0 * self.q2 + self.q1 * self.q3) + bz * (0.5 - q1q1 - q2q2)

            # 误差是估计方向与测量方向的叉积
            halfex = (ay * halfvz - az * halfvy) + (my * halfwz - mz * halfwy)
            halfey = (az * halfvx - ax * halfvz) + (mz * halfwx - mx * halfwz)
            halfez = (ax * halfvy - ay * halfvx) + (mx * halfwy - my * halfwx)

            # 计算并应用积分反馈
            if self.twoKi > 0.0:
                self.integralFBx += self.twoKi * halfex * deltat
                self.integralFBy += self.twoKi * halfey * deltat
                self.integralFBz += self.twoKi * halfez * deltat
                gx += self.integralFBx
                gy += self.integralFBy
                gz += self.integralFBz
            else:
                self.integralFBx = 0.0
                self.integralFBy = 0.0
                self.integralFBz = 0.0

            # 应用比例反馈
            gx += self.twoKp * halfex
            gy += self.twoKp * halfey
            gz += self.twoKp * halfez

        # 四元数积分
        gx *= (0.5 * deltat)
        gy *= (0.5 * deltat)
        gz *= (0.5 * deltat)
        qa = self.q0
        qb = self.q1
        qc = self.q2
        self.q0 += (-qb * gx - qc * gy - self.q3 * gz)
        self.q1 += (qa * gx + qc * gz - self.q3 * gy)
        self.q2 += (qa * gy - qb * gz + self.q3 * gx)
        self.q3 += (qa * gz + qb * gy - qc * gx)

        # 归一化四元数
        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3)
        self.q0 *= recipNorm
        self.q1 *= recipNorm
        self.q2 *= recipNorm
        self.q3 *= recipNorm
        self.anglesComputed = False

    def MahonyUpdateIMU(self, gx, gy, gz, ax, ay, az, deltat):
        """Mahony AHRS 算法更新（仅使用陀螺仪和加速度计）"""
        recipNorm = 0.0
        halfvx, halfvy, halfvz = 0.0, 0.0, 0.0
        halfex, halfey, halfez = 0.0, 0.0, 0.0
        qa, qb, qc = 0.0, 0.0, 0.0

        # 如果加速度计数据有效
        if not (ax == 0.0 and ay == 0.0 and az == 0.0):
            # 归一化加速度计数据
            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az)
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm

            # 估计重力方向
            halfvx = self.q1 * self.q3 - self.q0 * self.q2
            halfvy = self.q0 * self.q1 + self.q2 * self.q3
            halfvz = self.q0 * self.q0 - 0.5 + self.q3 * self.q3

            # 误差是估计方向与测量方向的叉积
            halfex = (ay * halfvz - az * halfvy)
            halfey = (az * halfvx - ax * halfvz)
            halfez = (ax * halfvy - ay * halfvx)

            # 计算并应用积分反馈
            if self.twoKi > 0.0:
                self.integralFBx += self.twoKi * halfex * deltat
                self.integralFBy += self.twoKi * halfey * deltat
                self.integralFBz += self.twoKi * halfez * deltat
                gx += self.integralFBx
                gy += self.integralFBy
                gz += self.integralFBz
            else:
                self.integralFBx = 0.0
                self.integralFBy = 0.0
                self.integralFBz = 0.0

            # 应用比例反馈
            gx += self.twoKp * halfex
            gy += self.twoKp * halfey
            gz += self.twoKp * halfez

        # 四元数积分
        gx *= (0.5 * deltat)
        gy *= (0.5 * deltat)
        gz *= (0.5 * deltat)
        qa = self.q0
        qb = self.q1
        qc = self.q2
        self.q0 += (-qb * gx - qc * gy - self.q3 * gz)
        self.q1 += (qa * gx + qc * gz - self.q3 * gy)
        self.q2 += (qa * gy - qb * gz + self.q3 * gx)
        self.q3 += (qa * gz + qb * gy - qc * gx)

        # 归一化四元数
        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3)
        self.q0 *= recipNorm
        self.q1 *= recipNorm
        self.q2 *= recipNorm
        self.q3 *= recipNorm
        self.anglesComputed = False

    def getRoll(self):
        """获取横滚角（度）"""
        if not self.anglesComputed:
            self.computeAngles()
        return math.degrees(self.roll)

    def getPitch(self):
        """获取俯仰角（度）"""
        if not self.anglesComputed:
            self.computeAngles()
        return math.degrees(self.pitch)

    def getYaw(self):
        """获取偏航角（度）"""
        if not self.anglesComputed:
            self.computeAngles()
        return math.degrees(self.yaw)

    def getRollRadians(self):
        """获取横滚角（弧度）"""
        if not self.anglesComputed:
            self.computeAngles()
        return self.roll

    def getPitchRadians(self):
        """获取俯仰角（弧度）"""
        if not self.anglesComputed:
            self.computeAngles()
        return self.pitch

    def getYawRadians(self):
        """获取偏航角（弧度）"""
        if not self.anglesComputed:
            self.computeAngles()
        return self.yaw

    def getQuat(self):
        """获取四元数"""
        return [self.q0, self.q1, self.q2, self.q3]
    
if __name__ == '__main__':

    sf = SensorFusion()

    # 示例：更新传感器数据
    gx, gy, gz = 0.1, 0.2, 0.3  # 陀螺仪数据
    ax, ay, az = 0.0, 0.0, 1.0  # 加速度计数据
    mx, my, mz = 0.0, 0.0, 0.0  # 磁力计数据

    # 更新传感器数据
    deltat = 0.01  # 时间间隔

    sf.MahonyUpdateIMU(gx, gy, gz, ax, ay, az, deltat)
    #sf.MahonyUpdate(gx, gy, gz, ax, ay, az, mx, my, mz, deltat)

    # 获取欧拉角
    roll = sf.getRoll()
    pitch = sf.getPitch()
    yaw = sf.getYaw()

    print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")