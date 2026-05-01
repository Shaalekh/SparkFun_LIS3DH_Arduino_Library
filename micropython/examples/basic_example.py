# basic_example.py
# Raspberry Pi Pico — LIS3DH minimal I2C example
#
# Wiring (I2C bus 0, default Pico pins):
#   LIS3DH SDA  →  GP4  (pin 6)
#   LIS3DH SCL  →  GP5  (pin 7)
#   LIS3DH VCC  →  3V3  (pin 36)
#   LIS3DH GND  →  GND  (pin 38)
#   LIS3DH SDO/SA0 → leave floating or tie to GND for address 0x18,
#                    or tie to 3V3 for address 0x19 (default)
#
# Copy lis3dh.py to the Pico (same folder as this file), then run this
# script in Thonny (Run → Run current script, or press F5).

from machine import I2C, Pin
import utime
from lis3dh import LIS3DH

# Initialise I2C
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)

# Create driver and start the sensor
imu = LIS3DH(i2c=i2c)       # address defaults to 0x19
imu.begin()                  # raises LIS3DHError if sensor not found

print("LIS3DH ready.\n")

while True:
    x, y, z = imu.read_accel()
    print("X: {:7.4f} g   Y: {:7.4f} g   Z: {:7.4f} g".format(x, y, z))
    utime.sleep_ms(1000)
