# lis3dh.py
# MicroPython driver for the LIS3DH 3-axis accelerometer
#
# Ported from the SparkFun Arduino library by Marshall Taylor
# Original: https://github.com/sparkfun/SparkFun_LIS3DH_Arduino_Library
#
# Supports I2C and SPI on Raspberry Pi Pico (and other MicroPython boards).
#
# Released under the MIT License.

import ustruct
import utime
from micropython import const

# ---------------------------------------------------------------------------
# Register map
# ---------------------------------------------------------------------------
_STATUS_REG_AUX = const(0x07)
_OUT_ADC1_L     = const(0x08)
_OUT_ADC2_L     = const(0x0A)
_OUT_ADC3_L     = const(0x0C)
_WHO_AM_I       = const(0x0F)
_TEMP_CFG_REG   = const(0x1F)
_CTRL_REG1      = const(0x20)
_CTRL_REG2      = const(0x21)
_CTRL_REG3      = const(0x22)
_CTRL_REG4      = const(0x23)
_CTRL_REG5      = const(0x24)
_CTRL_REG6      = const(0x25)
_REFERENCE      = const(0x26)
_STATUS_REG2    = const(0x27)
_OUT_X_L        = const(0x28)
_OUT_Y_L        = const(0x2A)
_OUT_Z_L        = const(0x2C)
_FIFO_CTRL_REG  = const(0x2E)
_FIFO_SRC_REG   = const(0x2F)
_INT1_CFG       = const(0x30)
_INT1_SRC       = const(0x31)
_INT1_THS       = const(0x32)
_INT1_DURATION  = const(0x33)
_CLICK_CFG      = const(0x38)
_CLICK_SRC      = const(0x39)
_CLICK_THS      = const(0x3A)
_TIME_LIMIT     = const(0x3B)
_TIME_LATENCY   = const(0x3C)
_TIME_WINDOW    = const(0x3D)

_WHO_AM_I_VALUE = const(0x33)

# ODR (output data rate) register codes
_ODR_MAP = {
    1:    0x1,
    10:   0x2,
    25:   0x3,
    50:   0x4,
    100:  0x5,
    200:  0x6,
    400:  0x7,
    1600: 0x8,
    5000: 0x9,
}

# Full-scale range register codes
_RANGE_MAP = {2: 0x0, 4: 0x1, 8: 0x2, 16: 0x3}

# Divisors used to convert raw counts → g  (from original library)
_RANGE_DIVISOR = {2: 15987, 4: 7840, 8: 3883, 16: 1280}


class LIS3DHError(Exception):
    """Raised when communication with the sensor fails."""
    pass


class LIS3DH:
    """MicroPython driver for the LIS3DH 3-axis accelerometer.

    Supports both I2C and SPI on Raspberry Pi Pico (and any MicroPython board).

    I2C usage::

        from machine import I2C, Pin
        from lis3dh import LIS3DH

        i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
        imu = LIS3DH(i2c=i2c)
        imu.begin()
        x, y, z = imu.read_accel()

    SPI usage::

        from machine import SPI, Pin
        from lis3dh import LIS3DH

        spi = SPI(0, baudrate=1_000_000, polarity=1, phase=1,
                  sck=Pin(2), mosi=Pin(3), miso=Pin(4))
        cs  = Pin(5, Pin.OUT, value=1)
        imu = LIS3DH(spi=spi, cs=cs)
        imu.begin()
        x, y, z = imu.read_accel()
    """

    def __init__(self, i2c=None, spi=None, cs=None, address=0x19):
        """Initialise the driver.

        Pass *either* an ``i2c`` object (``machine.I2C``) **or** an ``spi``
        object (``machine.SPI``) together with the ``cs`` chip-select pin
        (``machine.Pin``).

        Args:
            i2c:     ``machine.I2C`` instance for I2C mode.
            spi:     ``machine.SPI`` instance for SPI mode.
            cs:      ``machine.Pin`` chip-select output (SPI mode only).
            address: I2C device address.  Default ``0x19``; alternate ``0x18``
                     (SA0 pin pulled low).
        """
        if i2c is None and spi is None:
            raise LIS3DHError("Provide either 'i2c' or 'spi'")
        if spi is not None and cs is None:
            raise LIS3DHError("SPI mode requires a 'cs' (chip-select) pin")

        self._i2c  = i2c
        self._spi  = spi
        self._cs   = cs
        self._addr = address

        # ---- default sensor settings ----
        # ADC / temperature
        self.adc_enabled  = True
        self.temp_enabled = True

        # Accelerometer
        self.accel_sample_rate = 50   # Hz — 0,1,10,25,50,100,200,400,1600,5000
        self.accel_range       = 2    # g  — 2, 4, 8, 16
        self.x_accel_enabled   = True
        self.y_accel_enabled   = True
        self.z_accel_enabled   = True

        # FIFO
        self.fifo_enabled   = False
        self.fifo_threshold = 20      # 0–32
        self.fifo_mode      = 0       # 0=bypass, 1=FIFO, 3=FIFO-until-full

        # Error counters (mirrors Arduino library)
        self.all_ones_counter  = 0
        self.non_success_counter = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def begin(self):
        """Connect to the sensor and apply current settings.

        Raises:
            LIS3DHError: if the WHO_AM_I register does not return ``0x33``.
        """
        utime.sleep_ms(10)
        who = self._read_register(_WHO_AM_I)
        if who != _WHO_AM_I_VALUE:
            raise LIS3DHError(
                "LIS3DH not found at I2C address 0x{:02X} — "
                "WHO_AM_I=0x{:02X} (expected 0x33).\n"
                "Run an I2C scanner to find the correct address, then pass it "
                "as: LIS3DH(i2c=i2c, address=0xXX)".format(self._addr, who)
            )
        self._apply_settings()

    def apply_settings(self):
        """Re-apply settings after changing any ``self.*`` attribute."""
        self._apply_settings()

    # ---- accelerometer -----------------------------------------------

    def read_raw_accel_x(self):
        """Return the raw signed 16-bit X-axis acceleration value."""
        return self._read_int16(_OUT_X_L)

    def read_raw_accel_y(self):
        """Return the raw signed 16-bit Y-axis acceleration value."""
        return self._read_int16(_OUT_Y_L)

    def read_raw_accel_z(self):
        """Return the raw signed 16-bit Z-axis acceleration value."""
        return self._read_int16(_OUT_Z_L)

    def read_float_accel_x(self):
        """Return X-axis acceleration in g (float)."""
        return self._calc_accel(self.read_raw_accel_x())

    def read_float_accel_y(self):
        """Return Y-axis acceleration in g (float)."""
        return self._calc_accel(self.read_raw_accel_y())

    def read_float_accel_z(self):
        """Return Z-axis acceleration in g (float)."""
        return self._calc_accel(self.read_raw_accel_z())

    def read_accel(self):
        """Return a ``(x, y, z)`` tuple of acceleration values in g."""
        return (
            self.read_float_accel_x(),
            self.read_float_accel_y(),
            self.read_float_accel_z(),
        )

    # ---- ADC ---------------------------------------------------------

    def read_adc1(self):
        """Return ADC channel 1 as a 10-bit unsigned value (0–1023)."""
        return self._read_adc(_OUT_ADC1_L)

    def read_adc2(self):
        """Return ADC channel 2 as a 10-bit unsigned value (0–1023)."""
        return self._read_adc(_OUT_ADC2_L)

    def read_adc3(self):
        """Return ADC channel 3 as a 10-bit unsigned value (0–1023).

        When ``temp_enabled`` is ``True`` this channel encodes temperature
        difference (1 LSB ≈ 1 °C relative).
        """
        return self._read_adc(_OUT_ADC3_L)

    # ---- FIFO --------------------------------------------------------

    def fifo_begin(self):
        """Configure and enable the FIFO using current ``fifo_*`` settings."""
        data = self._read_register(_FIFO_CTRL_REG)
        data &= 0x20
        data |= (self.fifo_mode & 0x03) << 6
        data |= self.fifo_threshold & 0x1F
        self._write_register(_FIFO_CTRL_REG, data)

        data = self._read_register(_CTRL_REG5)
        data &= 0xBF
        data |= (int(self.fifo_enabled) & 0x01) << 6
        self._write_register(_CTRL_REG5, data)

    def fifo_clear(self):
        """Drain and discard all samples currently in the FIFO."""
        while (self.fifo_get_status() & 0x20) == 0:
            self.read_raw_accel_x()
            self.read_raw_accel_y()
            self.read_raw_accel_z()

    def fifo_start_rec(self):
        """Restart FIFO recording (toggle mode bits off then on)."""
        data = self._read_register(_FIFO_CTRL_REG)
        data &= 0x3F
        self._write_register(_FIFO_CTRL_REG, data)

        data = self._read_register(_FIFO_CTRL_REG)
        data &= 0x3F
        data |= (self.fifo_mode & 0x03) << 6
        self._write_register(_FIFO_CTRL_REG, data)

    def fifo_get_status(self):
        """Return the FIFO_SRC_REG byte.

        Bit 7 — watermark reached.
        Bit 6 — FIFO overrun.
        Bit 5 — FIFO empty.
        Bits 4:0 — number of unread samples.
        """
        return self._read_register(_FIFO_SRC_REG)

    def fifo_end(self):
        """Switch the FIFO back to bypass (off) mode."""
        data = self._read_register(_FIFO_CTRL_REG)
        data &= 0x3F
        self._write_register(_FIFO_CTRL_REG, data)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_settings(self):
        """Write the current settings to the sensor registers."""
        # TEMP_CFG_REG — enable ADC and/or temperature
        data = (int(self.temp_enabled) << 6) | (int(self.adc_enabled) << 7)
        self._write_register(_TEMP_CFG_REG, data)

        # CTRL_REG1 — ODR and axis enables
        odr  = _ODR_MAP.get(self.accel_sample_rate, 0x7)   # default 400 Hz
        data = (odr << 4) | (int(self.z_accel_enabled) << 2) | \
               (int(self.y_accel_enabled) << 1) | int(self.x_accel_enabled)
        self._write_register(_CTRL_REG1, data)

        # CTRL_REG4 — full-scale, block-data-update, high-resolution
        fs   = _RANGE_MAP.get(self.accel_range, 0x3)       # default ±16 g
        data = 0x80 | 0x08 | (fs << 4)                     # BDU=1, HR=1
        self._write_register(_CTRL_REG4, data)

    def _calc_accel(self, raw):
        """Convert a raw 16-bit value to g using the current range."""
        divisor = _RANGE_DIVISOR.get(self.accel_range, 1)
        return raw / divisor

    def _read_adc(self, reg):
        """Read one of the 10-bit ADC channels (same conversion as Arduino)."""
        raw      = self._read_int16(reg)
        raw      = -raw
        unsigned = raw + 32768
        return unsigned >> 6

    # ---- low-level register I/O --------------------------------------

    def _read_register(self, reg):
        """Read a single byte from *reg*."""
        if self._i2c:
            self._i2c.writeto(self._addr, bytes([reg]))
            return self._i2c.readfrom(self._addr, 1)[0]
        else:
            self._cs(0)
            self._spi.write(bytes([reg | 0x80]))
            result = bytearray(1)
            self._spi.readinto(result, 0x00)
            self._cs(1)
            return result[0]

    def _write_register(self, reg, value):
        """Write *value* (single byte) to *reg*."""
        if self._i2c:
            self._i2c.writeto(self._addr, bytes([reg, value]))
        else:
            self._cs(0)
            self._spi.write(bytes([reg & 0x7F, value]))
            self._cs(1)

    def _read_register_region(self, reg, length):
        """Read *length* bytes starting at *reg* (auto-increment)."""
        if self._i2c:
            self._i2c.writeto(self._addr, bytes([reg | 0x80]))
            return self._i2c.readfrom(self._addr, length)
        else:
            self._cs(0)
            self._spi.write(bytes([reg | 0x80 | 0x40]))   # read + auto-inc
            result = bytearray(length)
            self._spi.readinto(result, 0x00)
            self._cs(1)
            return result

    def _read_int16(self, reg):
        """Read two bytes from *reg* and return a signed 16-bit integer."""
        data = self._read_register_region(reg, 2)
        return ustruct.unpack('<h', data)[0]
