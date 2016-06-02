import smbus
import time
import math

class SensorDataProvider(object):
        """Provides data from sensors"""

        # Power management registers
        power_mgmt_1 = 0x6b
        power_mgmt_2 = 0x6c

        bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
        address = 0x68       # This is the address value read via the i2cdetect command

        """
        (x / 1000.0) / 16.0) *90.0) *(pi / 180) = 0.0000981748 * x
        To scale accelerometer values to radians
        """
        aclScale = 0.0000981748
        windowSize = 5 #Number of readings to average over
        measureInterval = 0.0001 #increase this if reading fails

        def __init__(self):
            # Now wake the 6050 up as it starts in sleep mode
            #TODO: Check if the device will go to sleep mode automatically, this will cause problems
            self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)

        def getGyro(self):
            xSum = 0
            ySum = 0
            zSum = 0
            for x in range(0,self.windowSize):
                xSum += float(self.read_word_2c(0x43))
                ySum += float(self.read_word_2c(0x45))
                zSum += float(self.read_word_2c(0x47))
                time.sleep(self.measureInterval)

            gyro_xout = xSum / self.windowSize
            gyro_yout = ySum / self.windowSize
            gyro_zout = zSum / self.windowSize
            return (gyro_xout, gyro_yout, gyro_zout)

        def getAccelerometer(self):
            xSum = 0
            ySum = 0
            zSum = 0
            for x in range(0, self.windowSize):
                xSum += float(self.read_word_2c(0x3b))
                ySum += float(self.read_word_2c(0x3d))
                zSum += float(self.read_word_2c(0x3f))
                time.sleep(self.measureInterval)

            accel_xout = xSum / self.windowSize
            accel_yout = ySum / self.windowSize
            accel_zout = zSum / self.windowSize
            return (accel_xout * self.aclScale, accel_yout * self.aclScale, accel_zout * self.aclScale)

        def read_byte(self, adr):
                return self.bus.read_byte_data(self.address, adr)

        def read_word(self, adr):
                high = self.bus.read_byte_data(self.address, adr)
                low = self.bus.read_byte_data(self.address, adr + 1)
                val = (high << 8) + low
                return val

        def read_word_2c(self, adr):
                val = self.read_word(adr)
                if (val >= 0x8000):
                        return -((65535 - val) + 1)
                else:
                        return val



        '''
        def dist(self, a,b):
            return math.sqrt((a*a)+(b*b))

        def get_y_rotation(self, x,y,z):
            radians = math.atan2(x, dist(y,z))
            return -math.degrees(radians)

        def get_x_rotation(self,x,y,z):
            radians = math.atan2(y, dist(x,z))
            return math.degrees(radians)

        '''
