from machine import I2C, Pin, ADC, Timer, SoftI2C
from time import sleep_ms, time_ns
from pico_i2c_lcd import I2cLcd
from bh1750 import BH1750

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

# i2c_2 = SoftI2C(scl=Pin(5), sda=Pin(4), freq=400000)
# light_sensor = BH1750(bus=i2c_2, addr=0x23)

led = Pin(25, mode=Pin.OUT)

adc = ADC(Pin(26, mode=Pin.IN))

counter = 0
voltage = 3.30
shutter_open = False
shutter_speed_ms = 0
shutter_start = 0
# lux = 0

def read_voltage():
    global adc
    val = adc.read_u16()
    val = val * (3.3 / 65535)
    return val

def update_display(timer):
    global counter
    global voltage
    global shutter_speed_ms
    global shutter_open
    global lux

    if shutter_open:
        return

    # led.toggle()

    lcd.clear()
    lcd.putstr(f"{voltage:.2f}V <> ")

    if shutter_speed_ms > 1000:
        lcd.putstr(f"{(shutter_speed_ms/1000):.2f}s")
    else:
        lcd.putstr(f"{shutter_speed_ms}ms")

    # led.toggle()

def shutter_timer_handler(timer):
    global shutter_open
    global shutter_speed_timer_ms

    if shutter_open:
        shutter_speed_timer_ms += 1
    else:
        del timer

def led_toggle(timer):
    global led

    led.toggle()

def read_lux(timer):
    global light_sensor
    global lux

    lux = light_sensor.luminance(BH1750.CONT_HIRES_1)
    sleep_ms(120)
    

def main_loop():
    global voltage
    global shutter_speed_ms
    global shutter_start
    global shutter_open

    threshold = 2

    while True:
        voltage = read_voltage()

        if voltage < threshold and not shutter_open:
            shutter_open = True
            shutter_speed_ms = 0
            shutter_start = time_ns()

        if voltage >= threshold and shutter_open:
            shutter_open = False
            shutter_speed_ms = (time_ns() - shutter_start) // 1_000_000

if __name__=="__main__":
    display_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=update_display)
    led_timer = Timer(mode=Timer.PERIODIC, period=100, callback=led_toggle)
    # light_sensor_timer = Timer(mode=Timer.PERIODIC, period=2000, callback=read_lux)
    main_loop()
    #_thread.start_new_thread(main_loop, ())
