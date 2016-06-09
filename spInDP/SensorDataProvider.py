import smbus
import time
import math
import threading


class SensorDataProvider(object):
    """Provides data from sensors attached to the spider."""

    # Power management registers
    POWER_MGMT_1 = 0x6b
    # POWER_MGMT_2 = 0x6c

    _bus = smbus.SMBus(1)
    BUS_ADDRESS = 0x68  # This is the address value read via the i2cdetect command

    """
    x / 16384 = x * 0.00006103515 to scale the accelerometer values from -1 to 1
    """
    ACL_SCALE = 0.00006103515

    """
    x / 131 = x * 0.00763358778 to scale gyro values to deg/second
    """
    GYRO_SCALE = 0.00763358778

    """Used for averaging"""
    _windowSize = 10  # Number of readings to average over
    _accelWindow = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
                    [0, 0, 0]]
    _cAccelIndex = 0

    _measureInterval = 0.1  # increase this if reading fails
    _shouldMeasure = False

    _smoothAccelX = 0.0
    _smoothAccelY = 0.0
    _smoothAccelZ = 0.0

    _lastUpdate = 0.0

    def __init__(self):
        """Initializes the SensorDataProvider."""
        # Now wake the 6050 up as it starts in sleep mode
        # TODO: Check if the device will go to sleep mode automatically, this will cause problems
        #self._bus.write_byte_data(SensorDataProvider.BUS_ADDRESS, SensorDataProvider.POWER_MGMT_1, 0)
        print ("Init sensordataprovider")

    def stopMeasuring(self):
        """Stop measuring the sensors."""
        
        self._shouldMeasure = False

    def startMeasuring(self):
        """Starts measuring the sensors."""

        if (not self._shouldMeasure):
            
            self._shouldMeasure = True
            self._lastUpdate = time.time()

            t = threading.Thread(target=self._measureCycle)
            t.start()

    def _measureCycle(self):
        """The measure loop."""

        while (self._shouldMeasure):

            accelVal = self.getAccelerometer()
            gyroVal = self.getGyro()

            yDeg = self._getXRotation(accelVal[0], accelVal[1], accelVal[2])
            gyroY = float(gyroVal[0])
            # print "yDeg: " + str(yDeg)

            """
            Complementary filter, we take gyroBias(0.98) parts from the gyro data and multiply it by delta T in seconds
            and accelBias(0.02) parts from accelerometer data to compensate for drift
            """

            deltaT = float(time.time() - self._lastUpdate)
            if (abs(gyroY * deltaT) < 0.05):
                gyroY = 0
            self._smoothAccelY = float(0.7 * float(self._smoothAccelY + gyroY * deltaT) - 0.3 * yDeg)
            # self.smoothAccelY = float(self.smoothAccelY + gyroY*deltaT)

            # self.smoothAccelY = float(self.smoothAccelY + gyroY*deltaT)
            print ("gyroY: " + str(self._smoothAccelY) + " delta: " + str(yDeg))
            self._lastUpdate = time.time()
            time.sleep(0.0016)  # Update at 60hz

    def getSmoothAccelerometer(self):
        """Gets the smoothed accelerometer value."""

        return self._smoothAccelX, self._smoothAccelY, self._smoothAccelZ

    def getGyro(self):
        """Gets the raw gyro sensor values."""

        gyro_xout = float(self._readWord2c(0x43))
        gyro_yout = float(self._readWord2c(0x45))
        gyro_zout = float(self._readWord2c(0x47))
        return (gyro_xout *
                SensorDataProvider.GYRO_SCALE, gyro_yout *
                SensorDataProvider.GYRO_SCALE, gyro_zout *
                SensorDataProvider.GYRO_SCALE)

    def getAccelerometer(self):
        """Gets the raw accelerometer sensor values."""

        accel_xout = float(self._readWord2c(0x3b))
        accel_yout = float(self._readWord2c(0x3d))
        accel_zout = float(self._readWord2c(0x3f))
        return accel_xout * \
               SensorDataProvider.ACL_SCALE, accel_yout * \
               SensorDataProvider.ACL_SCALE, accel_zout * \
               SensorDataProvider.ACL_SCALE

    def _readByte(self, adr):
        """Reads a byte from the sensor bus."""

        return self._bus.read_byte_data(SensorDataProvider.BUS_ADDRESS, adr)

    def _readWord(self, adr):
        """Reads a word from the sensor bus."""

        high = self._bus.read_byte_data(SensorDataProvider.BUS_ADDRESS, adr)
        low = self._bus.read_byte_data(SensorDataProvider.BUS_ADDRESS, adr + 1)
        val = (high << 8) + low
        return val

    def _readWord2c(self, adr):
        """Reads a word from the sensor bus."""

        val = self._readWord(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def _dist(self, a, b):
        """Calculates the length between two points on a triangle."""

        return math.sqrt((a * a) + (b * b))

    def _getYRotation(self, x, y, z):
        """Gets the Y rotation of the specified X, Y and Z."""

        radians = math.atan2(x, self._dist(y, z))
        return -math.degrees(radians)

    def _getXRotation(self, x, y, z):
        """Gets the X rotation of the specified X, Y and Z."""

        radians = math.atan2(y, self._dist(x, z))
        return math.degrees(radians)
