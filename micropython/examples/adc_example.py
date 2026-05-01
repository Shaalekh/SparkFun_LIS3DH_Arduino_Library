# adc_example.py
# Raspberry Pi Pico — LIS3DH ADC / temperature example
#
# The LIS3DH has three auxiliary 10-bit ADC channels (ADC1–ADC3).
# When temperature sensing is enabled, ADC3 reflects temperature
# change relative to a baseline (1 LSB ≈ 1 °C).
#
# Wiring: same as basic_example.py (I2C)
#
# Copy lis3dh.py to the Pico, then run in Thonny.

from machine import I2C, Pin
import utime
from lis3dh import LIS3DH

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)

imu = LIS3DH(i2c=i2c)

# Enable ADC and temperature
imu.adc_enabled  = True
imu.temp_enabled = True

# Accelerometer still runs alongside ADC
imu.accel_sample_rate = 50
imu.accel_range       = 2

imu.begin()

print("LIS3DH ADC example\n")
print("Note: ADC3 encodes *temperature difference* when temp_enabled=True")
print("      (1 count ≈ 1 °C relative to power-on reference)\n")

while True:
    print("ADC1: {:4d}   ADC2: {:4d}   ADC3 / Temp-delta: {:4d}".format(
        imu.read_adc1(),
        imu.read_adc2(),
        imu.read_adc3(),
    ))
    utime.sleep_ms(1000)
