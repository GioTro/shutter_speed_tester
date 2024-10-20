from machine import I2C, Pin, ADC, Timer
from time import sleep_ms, time_ns
from pico_i2c_lcd import I2cLcd

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

adc = ADC(Pin(26, mode=Pin.IN))

counter = 0
voltage = 3.30
shutter_speed_ms = 0
shutter_start = 0


def read_voltage():
    global adc
    val = adc.read_u16()
    val = val * (3.3 / 65535)
    return val


def update_display(timer):
    global counter
    global voltage
    global shutter_speed_ms

    lcd.clear()
    lcd.putstr(f"V: {voltage:.2f}V\n")

    if shutter_speed_ms > 1000:
        lcd.putstr(f"S: {(shutter_speed_ms/1000):.2f}s")
    else:
        lcd.putstr(f"S: {shutter_speed_ms}ms")


def poll_voltage(timer):
    global voltage
    global shutter_speed_ms

    new_voltage = read_voltage()

    if voltage >= 3 and new_voltage < 3:
        shutter_speed_ms = 0

    if voltage < 3 and new_voltage < 3:
        shutter_speed_ms += 1

    voltage = new_voltage


def main_loop():
    global voltage
    global shutter_speed_ms
    global shutter_start

    while True:
        new_voltage = read_voltage()

        if voltage >= 3 and new_voltage < 3:
            shutter_speed_ms = 0
            shutter_start = time_ns()

        if voltage < 3 and new_voltage >= 3:
            shutter_speed_ms = (time_ns() - shutter_start) // 1_000_000

        voltage = new_voltage


if __name__ == "__main__":
    display_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=update_display)
    # voltage_timer = Timer(mode=Timer.PERIODIC, period=1, callback=poll_voltage)
    main_loop()
