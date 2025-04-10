from machine import Pin #导入Pin模块

LED=Pin(15,Pin.OUT) #构建led对象，GPIO46,输出
LED.value(1) #点亮LED，也可以使用led.on()

