'''
实验名称：ADC-电压测量
版本：v1.0
作者：WalnutPi
说明：通过对ADC数据采集，转化成电压在显示屏上显示。ADC精度12位（0~4095），测量电压0-3.3V。
'''

#导入相关模块
from machine import Pin,SoftI2C,ADC,Timer, PWM
import time

#构建ADC对象
adc = ADC(Pin(4)) 
adc.atten(ADC.ATTN_11DB) #开启衰减器，测量量程增大到3.3V

in1 = PWM(Pin(5,Pin.OUT), freq=100000, duty=0)
in2 = Pin(6,Pin.OUT, value=0)

in3 = PWM(Pin(10,Pin.OUT), freq=100000, duty=0)
in4 = Pin(9,Pin.OUT, value=0) 

in3.duty(912)

time.sleep(1)
in3.duty(100)

def ADC_Test(tim):

    rate = adc.read() / 4095
    
    v_pwm = int(rate * 1023)

    in3.duty(v_pwm)
    in1.duty(v_pwm)
    
    #计算电压值，获得的数据0-4095相当于0-3.3V，（'%.2f'%）表示保留2位小数
    print(f'raw data:{adc.read()} rate: {rate:.2}  voltage:{('%.2f'%(rate*3.3))}V')


#开启定时器
tim = Timer(1)
tim.init(period=20, mode=Timer.PERIODIC, callback=ADC_Test) #周期300ms