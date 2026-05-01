# fifo_example.py
# Raspberry Pi Pico — LIS3DH FIFO watermark example
#
# Configures the FIFO to buffer 20 samples, then prints them as CSV once
# the watermark is reached.  This is a direct port of the Arduino
# FifoExample sketch.
#
# Wiring: same as basic_example.py (I2C)
#
# Copy lis3dh.py to the Pico, then run in Thonny.

from machine import I2C, Pin
import utime
from lis3dh import LIS3DH

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)

imu = LIS3DH(i2c=i2c)

# Sensor settings
imu.adc_enabled        = False
imu.temp_enabled       = False
imu.accel_sample_rate  = 10    # Hz
imu.accel_range        = 2     # ±2 g
imu.x_accel_enabled    = True
imu.y_accel_enabled    = True
imu.z_accel_enabled    = True

# FIFO settings
imu.fifo_enabled   = True
imu.fifo_threshold = 20        # watermark at 20 samples
imu.fifo_mode      = 1         # 1 = FIFO mode

imu.begin()

print("Configuring FIFO...")
imu.fifo_begin()
print("Clearing FIFO...")
imu.fifo_clear()
imu.fifo_start_rec()
print("FIFO ready — waiting for watermark...\n")
print("sample,x,y,z")

sample_number = 0

while True:
    # Wait until the watermark flag (bit 7) is set
    while (imu.fifo_get_status() & 0x80) == 0:
        utime.sleep_ms(1)

    # Drain until FIFO is empty (bit 5 = 1)
    while (imu.fifo_get_status() & 0x20) == 0:
        x = imu.read_float_accel_x()
        y = imu.read_float_accel_y()
        z = imu.read_float_accel_z()
        print("{},{:.4f},{:.4f},{:.4f}".format(sample_number, x, y, z))
        sample_number += 1
