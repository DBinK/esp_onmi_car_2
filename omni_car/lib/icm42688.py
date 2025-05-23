import time
import struct
from machine import Pin, SPI

# Register addresses
ICM42688_DEVICE_CONFIG = 0x11  # Device configuration register
ICM42688_PWR_MGMT0 = 0x4E      # Power management control register 0
ICM42688_WHO_AM_I = 0x75       # Device identification register
ICM42688_ACCEL_DATA_X1 = 0x1F  # Accelerometer X-axis data high byte
ICM42688_ACCEL_DATA_X0 = 0x20  # Accelerometer X-axis data low byte
ICM42688_GYRO_DATA_X1 = 0x25   # Gyroscope X-axis data high byte
ICM42688_GYRO_DATA_X0 = 0x26   # Gyroscope X-axis data low byte
ICM42688_REG_BANK_SEL = 0x76   # Register bank selection register
ICM42688_TEMP_DATA1 = 0x1D     # Temperature data high byte

# Bitmasks for configuration
ICM42688_PWR_TEMP_ON = 0 << 5         # Temperature sensor enabled
ICM42688_PWR_TEMP_OFF = 1 << 5        # Temperature sensor disabled
ICM42688_PWR_GYRO_MODE_LN = 3 << 2    # Gyroscope low noise mode
ICM42688_PWR_ACCEL_MODE_LN = 3 << 0   # Accelerometer low noise mode

ICM42688_GFS_2000DPS = 0x00 << 5  # Gyroscope full scale range set to 2000 degrees per second
ICM42688_AFS_16G = 0x00 << 5      # Accelerometer full scale range set to 16G
ICM42688_GODR_1kHz = 0x06         # Gyroscope output data rate set to 1 kHz
ICM42688_AODR_1kHz = 0x06         # Accelerometer output data rate set to 1 kHz

# Timeout for SPI communication (in seconds)
SPI_TIMEOUT = 0.5


class ICM42688P:
    def __init__(self, spi, cs_pin):
        # SPI and CS pin setup
        self.spi = spi
        self.cs = Pin(cs_pin, Pin.OUT, value=1)
        self.accel_scale = 16.0  # Default scale for accelerometer (16G)
        self.gyro_scale = 2000.0  # Default scale for gyroscope (2000 DPS)

    def _write_register(self, reg, value):
        """Write a byte to a specific register."""
        self.cs.value(0)
        self.spi.write(bytearray([reg & 0x7F, value]))
        self.cs.value(1)

    def _read_register(self, reg):
        """Read a byte from a specific register."""
        self.cs.value(0)
        self.spi.write(bytearray([reg | 0x80]))
        result = bytearray(1)
        self.spi.readinto(result)
        self.cs.value(1)
        return result[0]

    def _read_multiple_registers(self, reg, length):
        """Read multiple bytes starting from a specific register."""
        self.cs.value(0)
        self.spi.write(bytearray([reg | 0x80]))
        result = bytearray(length)
        self.spi.readinto(result)
        self.cs.value(1)
        return result

    def initialize(self):
        """Initialize the sensor."""
        # Reset the device
        self._write_register(ICM42688_REG_BANK_SEL, 0x00)  # Select bank 0
        self._write_register(ICM42688_DEVICE_CONFIG, 0x01)  # Reset
        time.sleep(0.1)

        # Verify WHO_AM_I register
        who_am_i = self._read_register(ICM42688_WHO_AM_I)
        if who_am_i != 0x47:
            raise RuntimeError(f"Unexpected WHO_AM_I value: 0x{who_am_i:02X}")
        print("ICM42688P initialized successfully!")

        # Enable all sensors
        self._write_register(
            ICM42688_PWR_MGMT0,
            ICM42688_PWR_TEMP_ON | ICM42688_PWR_GYRO_MODE_LN | ICM42688_PWR_ACCEL_MODE_LN,
        )
        time.sleep(0.05)

        # Configure accelerometer and gyroscope
        self.configure_accelerometer()
        self.configure_gyroscope()

    def configure_accelerometer(self, scale=ICM42688_AFS_16G, odr=ICM42688_AODR_1kHz):
        """Configure the accelerometer."""
        self.accel_scale = 16.0  # Default full scale is 16G
        self._write_register(0x50, scale | odr)  # ACCEL_CONFIG0

    def configure_gyroscope(self, scale=ICM42688_GFS_2000DPS, odr=ICM42688_GODR_1kHz):
        """Configure the gyroscope."""
        self.gyro_scale = 2000.0  # Default full scale is 2000 DPS
        self._write_register(0x4F, scale | odr)  # GYRO_CONFIG0

    def read_accelerometer(self):
        """Read accelerometer raw data and convert to G."""
        data = self._read_multiple_registers(ICM42688_ACCEL_DATA_X1, 6)
        accel_x = struct.unpack(">h", data[0:2])[0]
        accel_y = struct.unpack(">h", data[2:4])[0]
        accel_z = struct.unpack(">h", data[4:6])[0]

        # Convert to G based on scale
        accel_x = (accel_x / 32768.0) * self.accel_scale
        accel_y = (accel_y / 32768.0) * self.accel_scale
        accel_z = (accel_z / 32768.0) * self.accel_scale

        return accel_x, accel_y, accel_z

    def read_gyroscope(self):
        """Read gyroscope raw data and convert to DPS."""
        data = self._read_multiple_registers(ICM42688_GYRO_DATA_X1, 6)
        gyro_x = struct.unpack(">h", data[0:2])[0]
        gyro_y = struct.unpack(">h", data[2:4])[0]
        gyro_z = struct.unpack(">h", data[4:6])[0]

        # Convert to DPS based on scale
        gyro_x = (gyro_x / 32768.0) * self.gyro_scale
        gyro_y = (gyro_y / 32768.0) * self.gyro_scale
        gyro_z = (gyro_z / 32768.0) * self.gyro_scale

        return gyro_x, gyro_y, gyro_z

    def read_temperature(self):
        """Read temperature data."""
        data = self._read_multiple_registers(ICM42688_TEMP_DATA1, 2)
        temp_raw = struct.unpack(">h", data)[0]
        temperature = (temp_raw / 132.48) + 25.0  # Convert to Celsius
        return temperature


# Example usage
if __name__ == "__main__":
    
    spi = SPI(1, sck=Pin(3), mosi=Pin(5), miso=Pin(7))
    
    cs_pin = 9  # Replace with your actual CS pin number
    
    imu = ICM42688P(spi, cs_pin)
    imu.initialize()

    while True:
        accel_x, accel_y, accel_z = imu.read_accelerometer()
        gyro_x, gyro_y, gyro_z = imu.read_gyroscope()
        temp = imu.read_temperature()

        #print(f"Accel: X={accel_x:.2f} G, Y={accel_y:.2f} G, Z={accel_z:.2f} G")
        print(f"Gyro: X={gyro_x:.2f} DPS, Y={gyro_y:.2f} DPS, Z={gyro_z:.2f} DPS")
        #print(f"Temperature: {temp:.2f} C")
        time.sleep(0.0001)