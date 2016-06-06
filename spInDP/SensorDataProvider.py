import smbus
import time
import math
import threading

class SensorDataProvider(object):
        """Provides data from sensors"""

        # Power management registers
        power_mgmt_1 = 0x6b
        power_mgmt_2 = 0x6c

        bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
        address = 0x68       # This is the address value read via the i2cdetect command

        """
        x / 16384 = x * 0.00006103515 to scale the accelerometer values from -1 to 1
        """
        aclScale = 0.00006103515
        
        """
        x / 131 = x * 0.00763358778 to scale gyro values to deg/second 
        """
        gyroScale = 0.00763358778
        
        """Used for averaging"""
        windowSize = 10 #Number of readings to average over
        accelWindow = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        cAccelIndex = 0
        
        measureInterval = 0.1 #increase this if reading fails
        shouldMeasure = False
        
        smoothAccelX = 0.0
        smoothAccelY = 0.0
        smoothAccelZ = 0.0
        
        lastUpdate = 0.0;
        

        def __init__(self):
            # Now wake the 6050 up as it starts in sleep mode
            #TODO: Check if the device will go to sleep mode automatically, this will cause problems
            self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)
            self.startMeasuring()
            
        def stopMeasuring(self):
            self.shouldMeasure = False
        
        def startMeasuring(self):
            if(not self.shouldMeasure):
            
                self.shouldMeasure = True
                self.lastUpdate = time.time()
                t = threading.Thread(target=self.measureCycle)
                t.start()
        
        def measureCycle(self):
            while(self.shouldMeasure):
                                    
                accelVal = self.getAccelerometer()
                gyroVal = self.getGyro()
                
                yDeg = self.get_y_rotation(accelVal[0],accelVal[1],accelVal[2])
                gyroY = float(gyroVal[1])
                #print "yDeg: " + str(yDeg)              
                
                """
                Complementary filter, we take gyroBias(0.98) parts from the gyro data and multiply it by delta T in seconds
                and accelBias(0.02) parts from accelerometer data to compensate for drift
                """
                
               
                
                deltaT = float(time.time() - self.lastUpdate)
                self.smoothAccelY = float(0.98*float(self.smoothAccelY + gyroY*deltaT) + 0.02*yDeg)
                #print "compY: " + str(self.smoothAccelY)


                self.lastUpdate = time.time()
                
                
        def getSmoothAccelerometer(self):
            return self.smoothAccelX, self.smoothAccelY, self.smoothAccelZ
                
        def getGyro(self):
            gyro_xout = float(self.read_word_2c(0x43))
            gyro_yout = float(self.read_word_2c(0x45))
            gyro_zout = float(self.read_word_2c(0x47))
            return (gyro_xout * self.gyroScale, gyro_yout * self.gyroScale, gyro_zout * self.gyroScale)

        def getAccelerometer(self):
            accel_xout = float(self.read_word_2c(0x3b))
            accel_yout = float(self.read_word_2c(0x3d))
            accel_zout = float(self.read_word_2c(0x3f))
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

        def dist(self, a,b):
            return math.sqrt((a*a)+(b*b))

        def get_y_rotation(self, x,y,z):
            radians = math.atan2(x, self.dist(y,z))
            return -math.degrees(radians)

        def get_x_rotation(self,x,y,z):
            radians = math.atan2(y, self.dist(x,z))
            return math.degrees(radians)
