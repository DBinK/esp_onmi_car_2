import time
import struct
from machine import Pin, ADC

from modules.utils import debounce, map_value


class Button:
    def __init__(self, pin, callback):

        self.pin = pin
        self.callback = callback

        self.key = Pin(self.pin, Pin.IN, Pin.PULL_UP)
        self.key.irq(self.callback, Pin.IRQ_FALLING | Pin.IRQ_RISING)

    def read(self):
        try:
            return self.key.value()
        except AttributeError:
            raise ValueError("KEY is not properly initialized")


class Joystick:
    def __init__(self, x_pin, y_pin):
        self.x_pin = x_pin
        self.y_pin = y_pin
        self.x_axis = ADC(Pin(self.x_pin))
        self.y_axis = ADC(Pin(self.y_pin))
        self.x_axis.atten(ADC.ATTN_0DB)  # 按需开启衰减器，测量量程增大到3.3V
        self.y_axis.atten(ADC.ATTN_0DB)

    def read_raw(self):
        try:
            x_value = self.x_axis.read()
            y_value = self.y_axis.read()
            return x_value, y_value
        
        except Exception as e:
            print(f"Error reading ADC values: {e}")
            return 0, 0
    
    def read(self): 
        x_value, y_value = self.read_raw()
        
        x_value = int(map_value(self, x_value, (0, 4095), (0, 255)))
        y_value = int(map_value(self, y_value, (0, 4095), (0, 255)))

        # print(f"x_value: {x_value}, y_value: {y_value}")  # 输出摇杆数据
        
        return x_value, y_value  # uint8


class Gamepad:
    def __init__(self, debug=False):
        self.debug = debug
        self.init_inputs()

        # id, lx, ly, rx, ry, abxy & dpad, ls & rs & start & back, mode
        self.data = [1, 0,0, 0,0, 8,0, 6]  # 默认数据举例

    def set_bit(self, num, bit_position, value):
        """
        设置num在二进制表示中指定位置的位为1或0
        """
        if bit_position < 0 or bit_position > 7:
            raise ValueError("bit_position must be between 0 and 7")
        if value == 0:    # 按下
            return num | (1 << bit_position)  
        elif value == 1:  # 释放
            return num & ~(1 << bit_position) 
        
    def init_inputs(self):
        """初始化输入设备，包括按键和摇杆。"""
        self.up    = Button(10, self.up_callback)
        self.down  = Button(11, self.down_callback)
        self.left  = Button(12, self.left_callback)
        self.right = Button(13, self.right_callback)
        
        self.a  = Button(16, self.a_callback)
        self.b  = Button(21, self.b_callback)
        self.x  = Button(14, self.x_callback)
        self.y  = Button(15, self.y_callback)
        self.l1 = Button(6, self.l1_callback)
        self.r1 = Button(9, self.r1_callback)

        self.start = Button(0, self.start_callback)
        self.back  = Button(1, self.select_callback)

        self.ls = Joystick(4, 5)
        self.rs = Joystick(7, 8)

        self.DIRECTION_MAP = { # 定义方向键映射 (上,右,下,左)
            (0, 1, 1, 1): 0,   # 上
            (0, 0, 1, 1): 1,   # 上&右
            (1, 0, 1, 1): 2,   # 右
            (1, 0, 0, 1): 3,   # 右&下
            (1, 1, 0, 1): 4,   # 下
            (1, 1, 0, 0): 5,   # 下&左
            (1, 1, 1, 0): 6,   # 左
            (0, 1, 1, 0): 7,   # 左&上
            (1, 1, 1, 1): 8,   # 无按键按下
        }

    # dpad 方向键
    def update_direction(self):
        # 获取当前按键状态
        up = self.up.read()
        down = self.down.read()
        left = self.left.read()
        right = self.right.read()

        # 根据按键状态更新 
        key_state = (up, right, down, left)

        # print(key_state, self.DIRECTION_MAP.get(key_state, 8))  # 默认值为 8

        self.data[5] = self.data[5] & 0b11110000  # 清除方向键
        self.data[5] = self.data[5] | self.DIRECTION_MAP.get(key_state, 8)  # 设置方向键

    # 按键消抖时间
    key_timeout = 100_000
    
    # 方向键回调函数
    @debounce(key_timeout)
    def up_callback(self, KEY):
        self.update_direction() 

    @debounce(key_timeout)
    def down_callback(self, KEY):
        self.update_direction()

    @debounce(key_timeout)
    def left_callback(self, KEY):
        self.update_direction()

    @debounce(key_timeout)
    def right_callback(self, KEY):
        self.update_direction()

    # XABY 按键回调函数
    @debounce(key_timeout)
    def a_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 6, KEY.value())

    @debounce(key_timeout)
    def b_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 5, KEY.value())

    @debounce(key_timeout)
    def x_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 7, KEY.value())

    @debounce(key_timeout)
    def y_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 4, KEY.value())

    # L R & Start & Back 回调函数
    @debounce(key_timeout)
    def l1_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 7, KEY.value())

    @debounce(key_timeout)
    def r1_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 6, KEY.value())

    @debounce(key_timeout)
    def start_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 5, KEY.value())

    @debounce(key_timeout)
    def select_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 4, KEY.value())
    
    def read(self) -> list:
        """ 读取数据 """
        self.data[1], self.data[2] = self.ls.read()
        self.data[3], self.data[4] = self.rs.read()

        return self.data
    

    def list_to_binary_string(self, data_list):
        """ 将列表转换为二进制字符串 """
        format_string = 'B' * len(data_list)  # 设每个元素是一个8位无符号整数
        binary_data = struct.pack(format_string, *data_list)  # 打包成二进制数据
        
        return binary_data

    def read_bin(self):
        """ 读取二进制数据 """
        return self.list_to_binary_string(self.read())
    
    
if __name__ == "__main__":

    gamepad = Gamepad()

    while True: 
        data_bin = gamepad.read_bin()
        data = gamepad.data

        # print(f"bin: {data_bin}")
        print(f"raw: {data}, xaby: {bin((data[5] & 0b11110000) >> 4)}, other: {bin(data[6])}, dpad: {bin(data[5] & 0b00001111)}" )

        time.sleep(0.1)
    
