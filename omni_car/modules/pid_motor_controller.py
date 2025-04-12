# 
from machine import Timer

from modules import encoder
from modules import motor
from modules import pid

class Encoders:
    def __init__(self, pins):
        self.encoder_lf = encoder.Encoder(pins[0], pins[1])
        self.encoder_rf = encoder.Encoder(pins[2], pins[3])
        self.encoder_rb = encoder.Encoder(pins[4], pins[5])
        self.encoder_lb = encoder.Encoder(pins[6], pins[7])

        self.pos = [0, 0, 0, 0]
        self.speed = [0, 0, 0, 0]

        self.period = 0.001  # 1ms
        
        tim = Timer(-1)
        tim.init(period=self.period*1000, mode=Timer.PERIODIC,callback=self.update_rate)  # 1ms 计算一次速度

    def update_rate(self):
        # 计算速度
        self.encoder_lf.update_speed()
        self.encoder_rf.update_speed()
        self.encoder_rb.update_speed()
        self.encoder_lb.update_speed()

        self.pos[0] = self.encoder_lf.position()
        self.pos[1] = self.encoder_rf.position()
        self.pos[2] = self.encoder_rb.position()
        self.pos[3] = self.encoder_lb.position()

        self.speed[0] = self.encoder_lf.speed
        self.speed[1] = self.encoder_rf.speed
        self.speed[2] = self.encoder_rb.speed
        self.speed[3] = self.encoder_lb.speed

        # print(f"pos: {self.pos}, rate: {self.speed}")


if __name__ == "__main__":

    import time

    pins = [4, 6, 39, 40, 21, 34, 12, 11]
    encoders = Encoders(pins)

    while True:
        print(f"pos: {encoders.pos}, rate: {encoders.speed}")
        time.sleep(0.1)
