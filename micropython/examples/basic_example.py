# basic_example.py
# Raspberry Pi Pico — LIS3DH minimal I2C example
#
# Wiring (I2C bus 0, default Pico pins):
#   LIS3DH SDA  →  GP0  (pin 1)   ← Pico default for I2C0
#   LIS3DH SCL  →  GP1  (pin 2)
#   LIS3DH VCC  →  3V3  (pin 36)
#   LIS3DH GND  →  GND  (pin 38)
#
# STEP 1 — Find your sensor's I2C address
# ----------------------------------------
# Run the scanner below first to discover the address your breakout uses.
# Common addresses: 0x18, 0x19, 0x1D (depends on SA0/SDO wiring).
# Once you know the address, set it in SENSOR_ADDRESS below and proceed
# to the main program.
#
# Copy lis3dh.py to the Pico (same folder as this file), then run this
# script in Thonny (Run → Run current script, or press F5).

from machine import I2C, Pin
import utime
from lis3dh import LIS3DH

# -----------------------------------------------------------------------
# OPTIONAL: I2C scanner — uncomment this block if you are unsure of the
# sensor address, run it once, then comment it out again.
# -----------------------------------------------------------------------
# i2c_scan = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
# print("Scanning I2C bus 0 (SDA=GP0, SCL=GP1) …")
# devices = i2c_scan.scan()
# if devices:
#     for d in devices:
#         print("  Found device at 0x{:02X} ({})".format(d, d))
# else:
#     print("  No devices found — check wiring!")
# print("Scan complete — {} device(s) found.".format(len(devices)))
# -----------------------------------------------------------------------

# Set this to the address reported by the I2C scanner above.
# Common values: 0x19 (SA0 high), 0x18 (SA0 low), 0x1D (some breakouts)
SENSOR_ADDRESS = 0x19

# Initialise I2C on bus 0 using the default Pico pins (GP0/GP1)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)

# Create driver and start the sensor
imu = LIS3DH(i2c=i2c, address=SENSOR_ADDRESS)
imu.begin()   # raises LIS3DHError if sensor is not found at SENSOR_ADDRESS

print("LIS3DH ready.\n")

while True:
    x, y, z = imu.read_accel()
    print("X: {:7.4f} g   Y: {:7.4f} g   Z: {:7.4f} g".format(x, y, z))
    utime.sleep_ms(1000)
