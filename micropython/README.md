# LIS3DH MicroPython Library for Raspberry Pi Pico

MicroPython port of the [SparkFun LIS3DH Arduino Library](https://github.com/sparkfun/SparkFun_LIS3DH_Arduino_Library), targeting the **Raspberry Pi Pico** and compatible MicroPython boards.

## Features

- I²C and SPI communication
- Read X/Y/Z acceleration (raw counts or float in *g*)
- Three auxiliary 10-bit ADC channels
- Optional temperature delta channel (via ADC3)
- FIFO buffering with watermark support
- Fully configurable sample rate (1–5000 Hz) and range (±2/4/8/16 g)

---

## Files

| File | Description |
|------|-------------|
| `lis3dh.py` | Driver module — copy this to your Pico |
| `examples/basic_example.py` | Minimal I²C accelerometer read |
| `examples/spi_example.py` | SPI accelerometer read |
| `examples/adc_example.py` | ADC / temperature read |
| `examples/fifo_example.py` | FIFO watermark + CSV output |

---

## Installation (Thonny)

1. Flash **MicroPython** onto your Pico if you haven't already  
   (*Thonny → Help → Install MicroPython…*).
2. Open **`micropython/lis3dh.py`** in Thonny.
3. Choose **File → Save copy… → Raspberry Pi Pico** and save it as `lis3dh.py`.
4. Open the example you want to run, wire up the sensor (see below), then press **F5** (Run).

---

## Wiring

### I²C (default)

| LIS3DH pin | Pico pin | Pico GPIO |
|-----------|----------|-----------|
| VCC / VDD | 3V3 (pin 36) | — |
| GND       | GND (pin 38) | — |
| SDA       | Pin 6 | GP4 |
| SCL       | Pin 7 | GP5 |
| SDO / SA0 | 3V3 → address **0x19** (default) | — |
|           | GND → address **0x18** | — |

> You can use any I²C-capable pins; update `sda` and `scl` in your script accordingly.

### SPI

| LIS3DH pin | Pico pin | Pico GPIO |
|-----------|----------|-----------|
| VCC / VDD | 3V3 (pin 36) | — |
| GND       | GND (pin 38) | — |
| SCK / SPC | Pin 4 | GP2 |
| MOSI / SDI| Pin 5 | GP3 |
| MISO / SDO| Pin 6 | GP4 |
| CS  / ~CS | Pin 7 | GP5 |

> The LIS3DH SPI interface uses **mode 3** (CPOL=1, CPHA=1).

---

## Quick-start

### I²C

```python
from machine import I2C, Pin
from lis3dh import LIS3DH

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
imu = LIS3DH(i2c=i2c)
imu.begin()

x, y, z = imu.read_accel()   # returns (x, y, z) in g
print(x, y, z)
```

### SPI

```python
from machine import SPI, Pin
from lis3dh import LIS3DH

spi = SPI(0, baudrate=1_000_000, polarity=1, phase=1,
          sck=Pin(2), mosi=Pin(3), miso=Pin(4))
cs  = Pin(5, Pin.OUT, value=1)

imu = LIS3DH(spi=spi, cs=cs)
imu.begin()

x, y, z = imu.read_accel()
print(x, y, z)
```

---

## Configuration

Modify settings **before** calling `begin()`, or call `apply_settings()` after changing them at runtime.

```python
imu.accel_sample_rate = 100   # Hz: 1, 10, 25, 50, 100, 200, 400, 1600, 5000
imu.accel_range       = 4     # g: 2, 4, 8, 16
imu.adc_enabled       = True
imu.temp_enabled      = True  # ADC3 becomes temperature-delta channel
imu.begin()
```

---

## API Reference

### Constructor

```python
LIS3DH(i2c=None, spi=None, cs=None, address=0x19)
```

### Methods

| Method | Description |
|--------|-------------|
| `begin()` | Verify sensor and apply settings. Raises `LIS3DHError` on failure. |
| `apply_settings()` | Re-apply settings after runtime changes. |
| `read_accel()` | `(x, y, z)` tuple in g. |
| `read_float_accel_x/y/z()` | Single-axis float in g. |
| `read_raw_accel_x/y/z()` | Raw signed 16-bit value. |
| `read_adc1/2/3()` | 10-bit ADC value (0–1023). |
| `fifo_begin()` | Configure FIFO with current `fifo_*` settings. |
| `fifo_clear()` | Drain and discard FIFO contents. |
| `fifo_start_rec()` | Restart FIFO recording. |
| `fifo_get_status()` | Return `FIFO_SRC_REG` byte. |
| `fifo_end()` | Switch FIFO to bypass (off). |

### Attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| `accel_sample_rate` | `50` | Output data rate in Hz |
| `accel_range` | `2` | Full-scale range in g |
| `x/y/z_accel_enabled` | `True` | Enable individual axes |
| `adc_enabled` | `True` | Enable ADC channels |
| `temp_enabled` | `True` | Enable temperature via ADC3 |
| `fifo_enabled` | `False` | Enable FIFO |
| `fifo_threshold` | `20` | FIFO watermark (0–32) |
| `fifo_mode` | `0` | 0=bypass, 1=FIFO, 3=FIFO-until-full |

---

## License

MIT — see [LICENSE.md](../LICENSE.md).
