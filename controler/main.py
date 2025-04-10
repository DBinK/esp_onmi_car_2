# 标准库
import time
import json
import network
import _thread
import espnow
from machine import Pin, ADC

# 本地库
import modules.gamepad as gamepad
import modules.lcd as lcd
from modules.utils import TimeDiff


print("正在启动...") 
time.sleep(2)  # 防止点停止按钮后马上再启动导致 Thonny 连接不上

# 初始化 wifi
sta = network.WLAN(network.STA_IF)  # 或者使用 network.AP_IF
sta.active(True)
sta.disconnect()  # 对于 ESP8266

# 初始化 espnow
now = espnow.ESPNow()
now.active(True)
peer = b"\xff\xff\xff\xff\xff\xff"  # 使用广播地址
now.add_peer(peer)

# 构建手柄对象
gamepad = gamepad.Gamepad()
main_dt = TimeDiff()

gamepad_data = []
diff = 1_000_000  #随便初始化一个数


def data_to_json(data):
    data_dict = {
        "ID": data[0],
        "LX": data[1],
        "LY": data[2],
        "RX": data[3],
        "RY": data[4],
        "XABY/Pad": data[5],
        "LS/RS/Start/Back": data[6],
        "mode": data[7],
    }
    
    print(data_dict)
    
    return json.dumps(data_dict)

def show_lcd():
    global gamepad_data, diff_ns
    
    time.sleep(1)  # 延时1秒, 不然不显示

    while True:

        lcd.show_gamepad(gamepad_data, diff_ns)  #lcd显示数据

        time.sleep(0.1) 


def send_espnow():
    global gamepad_data, peer, diff_ns

    while True:
        gamepad_data = gamepad.read()

        # data_json = data_to_json(data)  # 将数据转换为 JSON 字符串并发送

        data_json = json.dumps(gamepad_data)      # 将列表直接转换为 JSON 字符串

        now.send(peer, data_json) 
        print(f"发送数据: {gamepad_data}") 

        diff_ns = main_dt.time_diff() 
        print(f"延迟ms: {diff_ns / 1000_000}, 频率Hz: {1_000_000_000 / diff_ns}")
        
        #lcd.show_gamepad(gamepad_data, diff_ns)  #lcd显示数据
        
        time.sleep(0.001)
        
        # time.sleep(1) 


def main():
    _thread.start_new_thread(send_espnow, ())
    _thread.start_new_thread(show_lcd, ())

    while True:
        time.sleep(1)  # 主线程保持运行


# 运行主函数
main()