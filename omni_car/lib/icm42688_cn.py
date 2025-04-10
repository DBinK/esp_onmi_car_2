import time
import math
import struct
from machine import Pin, SPI

# 寄存器地址
ICM42688_DEVICE_CONFIG = 0x11         # 设备配置寄存器地址
ICM42688_PWR_MGMT0 = 0x4E             # 电源管理寄存器地址
ICM42688_WHO_AM_I = 0x75              # 设备ID寄存器地址
ICM42688_ACCEL_DATA_X1 = 0x1F         # 加速度计X轴数据寄存器地址（高8位）
ICM42688_ACCEL_DATA_X0 = 0x20         # 加速度计X轴数据寄存器地址（低8位）
ICM42688_GYRO_DATA_X1 = 0x25          # 陀螺仪X轴数据寄存器地址（高8位）
ICM42688_GYRO_DATA_X0 = 0x26          # 陀螺仪X轴数据寄存器地址（低8位）
ICM42688_REG_BANK_SEL = 0x76          # 寄存器库选择地址
ICM42688_TEMP_DATA1 = 0x1D            # 温度数据寄存器地址（高8位）

# 配置用的位掩码
ICM42688_PWR_TEMP_ON = 0 << 5         # 电源管理：温度传感器开启
ICM42688_PWR_TEMP_OFF = 1 << 5        # 电源管理：温度传感器关闭
ICM42688_PWR_GYRO_MODE_LN = 3 << 2    # 电源管理：陀螺仪低噪声模式
ICM42688_PWR_ACCEL_MODE_LN = 3 << 0   # 电源管理：加速度计低噪声模式

ICM42688_GFS_2000DPS = 0x00 << 5      # 陀螺仪满量程范围：2000度/秒
ICM42688_AFS_16G = 0x00 << 5          # 加速度计满量程范围：16g
ICM42688_GODR_1kHz = 0x06             # 陀螺仪输出数据速率：1kHz
ICM42688_AODR_1kHz = 0x06             # 加速度计输出数据速率：1kHz

# SPI通信超时时间（秒）
SPI_TIMEOUT = 0.5


class ICM42688P:
    def __init__(self, spi, cs_pin):
        """初始化SPI和片选引脚"""
        self.spi = spi
        self.cs = Pin(cs_pin, Pin.OUT, value=1)
        self.accel_scale = 16.0   # 默认加速度计量程 (16G)
        self.gyro_scale = 2000.0  # 默认陀螺仪量程 (2000 DPS)

    def _write_register(self, reg, value):
        """向特定寄存器写入一个字节"""
        self.cs.value(0)
        self.spi.write(bytearray([reg & 0x7F, value]))
        self.cs.value(1)

    def _read_register(self, reg):
        """从特定寄存器读取一个字节"""
        self.cs.value(0)
        self.spi.write(bytearray([reg | 0x80]))
        result = bytearray(1)
        self.spi.readinto(result)
        self.cs.value(1)
        return result[0]

    def _read_multiple_registers(self, reg, length):
        """从特定寄存器开始读取多个字节"""
        self.cs.value(0)
        self.spi.write(bytearray([reg | 0x80]))
        result = bytearray(length)
        self.spi.readinto(result)
        self.cs.value(1)
        return result

    def initialize(self):
        """初始化传感器"""
        # 复位设备
        self._write_register(ICM42688_REG_BANK_SEL, 0x00)   # 选择银行0
        self._write_register(ICM42688_DEVICE_CONFIG, 0x01)  # 复位
        time.sleep(0.1)

        # 校验WHO_AM_I寄存器
        who_am_i = self._read_register(ICM42688_WHO_AM_I)
        if who_am_i != 0x47:
            raise RuntimeError(f"意外的WHO_AM_I值: 0x{who_am_i:02X}")
        # print(f"ICM42688P初始化成功！WHO_AM_I值: 0x{who_am_i:02X}")

        # 启用所有传感器
        self._write_register(
            ICM42688_PWR_MGMT0,
            ICM42688_PWR_TEMP_ON | ICM42688_PWR_GYRO_MODE_LN | ICM42688_PWR_ACCEL_MODE_LN,
        )
        time.sleep(0.05)

        # 配置加速度计和陀螺仪
        self.configure_accelerometer()
        self.configure_gyroscope()

    def configure_accelerometer(self, scale=ICM42688_AFS_16G, odr=ICM42688_AODR_1kHz):
        """配置加速度计"""
        self.accel_scale = 16.0                  # 默认满量程为16G
        self._write_register(0x50, scale | odr)  # ACCEL_CONFIG0

    def configure_gyroscope(self, scale=ICM42688_GFS_2000DPS, odr=ICM42688_GODR_1kHz):
        """配置陀螺仪"""
        self.gyro_scale = 2000.0                 # 默认满量程为2000 DPS
        self._write_register(0x4F, scale | odr)  # GYRO_CONFIG0

    def read_accelerometer(self):
        """读取加速度计原始数据并转换为G"""
        data = self._read_multiple_registers(ICM42688_ACCEL_DATA_X1, 6)
        accel_x = struct.unpack(">h", data[0:2])[0]
        accel_y = struct.unpack(">h", data[2:4])[0]
        accel_z = struct.unpack(">h", data[4:6])[0]

        # 根据量程转换为G
        accel_x = (accel_x / 32768.0) * self.accel_scale
        accel_y = (accel_y / 32768.0) * self.accel_scale
        accel_z = (accel_z / 32768.0) * self.accel_scale

        return accel_x, accel_y, accel_z

    def read_gyroscope(self):
        """读取陀螺仪原始数据并转换为DPS"""
        data = self._read_multiple_registers(ICM42688_GYRO_DATA_X1, 6)
        gyro_x = struct.unpack(">h", data[0:2])[0]
        gyro_y = struct.unpack(">h", data[2:4])[0]
        gyro_z = struct.unpack(">h", data[4:6])[0]

        # 根据量程转换为DPS
        gyro_x = (gyro_x / 32768.0) * self.gyro_scale
        gyro_y = (gyro_y / 32768.0) * self.gyro_scale
        gyro_z = (gyro_z / 32768.0) * self.gyro_scale

        return gyro_x, gyro_y, gyro_z

    def read_temperature(self):
        """读取温度数据"""
        data = self._read_multiple_registers(ICM42688_TEMP_DATA1, 2)
        temp_raw = struct.unpack(">h", data)[0]
        temperature = (temp_raw / 132.48) + 25.0  # 转换为摄氏度
        return temperature



# 示例用法
if __name__ == "__main__":

    import math
    from modules.utils import TimeDiff
    
    import modules.fusion as fusion


    main_dt = TimeDiff()
    
    spi = SPI(1, sck=Pin(3), mosi=Pin(5), miso=Pin(7))
    
    cs_pin = 9  # 替换为实际的CS引脚编号
    
    imu = ICM42688P(spi, cs_pin)
    imu.initialize()

    led = Pin(15, Pin.OUT)
    led.value(1)

    fuse = fusion.Fusion()

    # 初始化yaw角
    yaw = 0.0
    
    DEG2RAD = math.pi / 180.0
    RAD2DEG = 180.0 / math.pi


    while True: 
        accel_x, accel_y, accel_z = imu.read_accelerometer()
        gyro_x, gyro_y, gyro_z = imu.read_gyroscope()
        # temp = imu.read_temperature()

        # 计算时间差
        dt = main_dt.time_diff() / 1_000_000_000  # 将ns转换为s
        Hz = int(1/dt) if dt > 0.0001 else 0  # 避免第一次的数很大
        
        # 对陀螺仪的z轴数据进行积分以计算yaw角
        yaw += gyro_z * dt
    
        # print(f"Yaw Angle: {yaw} , dt: {dt:.6f}, Hz: {int(1/dt)}")

        # 计算 pitch 和 roll
        pitch = math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)) * RAD2DEG
        roll  = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)) * RAD2DEG
    
        # 打印
        print(f"raw: {yaw=:.2f}, {pitch=:.2f}, {roll=:.2f}, {dt=:.3f}, {Hz=}")

        # 更新融合数据
        #fuse.update_nomag((accel_x, accel_y, accel_z), (gyro_x, gyro_y, gyro_z))
        #print(f"fuse: {fuse.heading:.2f}, {fuse.pitch:.2f}, {(180-fuse.roll):.2f}")

        #print(f"加速度: X={accel_x:.2f} G, Y={accel_y:.2f} G, Z={accel_z:.2f} G")
        #print(f"角速度: X={gyro_x:.2f} DPS, Y={gyro_y:.2f} DPS, Z={gyro_z:.2f} DPS")
        #print(f"温度: {temp:.2f} C")
        time.sleep(0.01)

        led.value(not led.value())   