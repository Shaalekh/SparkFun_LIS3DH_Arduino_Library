# spi_example.py
# Raspberry Pi Pico — LIS3DH SPI example
#
# Wiring (SPI bus 0):
#   LIS3DH SCK  →  GP2  (pin 4)
#   LIS3DH MOSI →  GP3  (pin 5)
#   LIS3DH MISO →  GP4  (pin 6)
#   LIS3DH CS   →  GP5  (pin 7)
#   LIS3DH VCC  →  3V3  (pin 36)
#   LIS3DH GND  →  GND  (pin 38)
#
# The LIS3DH SPI interface uses CPOL=1, CPHA=1 (mode 3).
#
# Copy lis3dh.py to the Pico (same folder as this file), then run this
# script in Thonny (Run → Run current script, or press F5).

from machine import SPI, Pin
import utime
from lis3dh import LIS3DH

# Initialise SPI — mode 3 (polarity=1, phase=1), 1 MHz
spi = SPI(0, baudrate=1_000_000, polarity=1, phase=1,
          sck=Pin(2), mosi=Pin(3), miso=Pin(4))

# Chip-select: idle HIGH
cs = Pin(5, Pin.OUT, value=1)

# Create driver and start the sensor
imu = LIS3DH(spi=spi, cs=cs)
imu.begin()                  # raises LIS3DHError if sensor not found

print("LIS3DH ready (SPI).\n")

while True:
    x, y, z = imu.read_accel()
    print("X: {:7.4f} g   Y: {:7.4f} g   Z: {:7.4f} g".format(x, y, z))
    utime.sleep_ms(1000)
