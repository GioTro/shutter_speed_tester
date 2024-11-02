import logger
from machine import I2C, Pin, ADC, Timer
from time import sleep_ms, time_ns
from ssd1306 import SSD1306_I2C

# setup led on board
led = Pin(25, mode=Pin.OUT)
led.on()

# variables
voltage: float = 3.30
shutter_open: bool = False
shutter_speed_ms: int = 0
shutter_start: int = 0

# setup
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = i2c.scan()[0]

# init display
oled = SSD1306_I2C(128, 32, i2c)

# set contrast
oled.contrast(64)

# setup adc pin
adc = ADC(Pin(26, mode=Pin.IN))

# flash led
for _ in range(5):
    led.toggle()
    sleep_ms(100)
led.off()

def read_voltage():
    global adc
    val = adc.read_u16()
    val = val * (3.3 / 65535)
    return val

def update_display(timer):
    global oled
    global voltage
    global shutter_speed_ms
    global shutter_open

    # clear Display
    oled.fill(0)

    # display voltage
    oled.text(f"{voltage:.2f} V", 5, 5)

    # format shutter speed
    s: str = f"{shutter_speed_ms} ms"

    if shutter_speed_ms >= 1000:
        # display shutter speed in seconds 
        s = f"{(shutter_speed_ms / 1000):.2f} s"

    if shutter_speed_ms == 0:
        s = "-"

    # display shutter speed 
    oled.text(f"S: {s}", 5, 25)

    oled.show()

def poll(timer):
    global voltage
    global shutter_speed_ms
    global shutter_start
    global shutter_open

    # voltage threshold
    threshold = 1

    voltage = read_voltage()

    if voltage >= threshold and not shutter_open:
        shutter_open = True
        shutter_start = time_ns()
        return

    if voltage < threshold and shutter_open:
        shutter_open = False
        shutter_speed_ms = (time_ns() - shutter_start) // 1_000_000

if __name__ == "__main__":
    display_timer = Timer(mode=Timer.PERIODIC, period=42, callback=update_display)
    poll = Timer(mode=Timer.PERIODIC, period=1, callback=poll)

