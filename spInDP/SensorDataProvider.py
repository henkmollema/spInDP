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
        (x / 1000.0) / 16.0) *90.0) *(pi / 180) = 0.0000981748 * x
        To scale accelerometer values to radians
        """
        aclScale = 0.0000981748
        
        
        
        """Used for averaging"""
        windowSize = 10 #Number of readings to average over
        accelWindow = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        
        cAccelIndex = 0
        
        measureInterval = 0.1 #increase this if reading fails
        shouldMeasure = False
        
        smoothAccelX = 0
        smoothAccelY = 0
        smoothAccelZ = 0
        
        """Used for Kalmanfilter"""
        Q_angle  =  0.1
        Q_gyro   =  0.003
        R_angle  =  0.1
        y_bias = 0
        YP_00 = 0
        YP_01 = 0
        YP_10 = 0
        YP_11 = 0
        KFangleY = 0.0
        
        def kalmanFilterY(self, accAngle, gyroRate, DT):
            y = 0
            S = 0
            K_0 = 0
            K_1 = 0
            
            self.KFangleY += DT * (gyroRate - self.y_bias);
            
            self.YP_00 +=  - DT * (self.YP_10 + self.YP_01) + self.Q_angle * DT;
            self.YP_01 +=  - DT * self.YP_11;
            self.YP_10 +=  - DT * self.YP_11;
            self.YP_11 +=  + self.Q_gyro * DT;
            
            y = accAngle - self.KFangleY;
            S = self.YP_00 + self.R_angle;
            K_0 = self.YP_00 / S;
            K_1 = self.YP_10 / S;
            
            self.KFangleY +=  K_0 * y;
            self.y_bias  +=  K_1 * y;
            self.YP_00 -= K_0 * self.YP_00;
            self.YP_01 -= K_0 * self.YP_01;
            self.YP_10 -= K_1 * self.YP_00;
            self.YP_11 -= K_1 * self.YP_01;
        
            return self.KFangleY;
        

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
                t = threading.Thread(target=self.measureCycle)
                t.start()
        
        def measureCycle(self):
            while(self.shouldMeasure):
                if(self.cAccelIndex + 1 >= self.windowSize):
                    self.cAccelIndex = 0
                    
                self.accelWindow[self.cAccelIndex] = self.getAccelerometer()
                
                xSum = 0
                ySum = 0
                zSum = 0
                for x in range(0, self.windowSize):
                    xSum += self.accelWindow[x][0]
                    ySum += self.accelWindow[x][1]
                    zSum += self.accelWindow[x][2]
                self.cAccelIndex += 1

                self.smoothAccelX = xSum / self.windowSize
                self.smoothAccelY = ySum / self.windowSize
                self.smoothAccelZ = zSum / self.windowSize
                
                
                # gyroValY = self.getGyro()[1]
                # AccelValY = self.getAccelerometer()[1]
                # self.smoothAccelY = self.kalmanFilterY(AccelValY, gyroValY, self.measureInterval)
                               
                # time.sleep(self.measureInterval)
                
                #print "SmoothY: " + str(self.smoothAccelY * 180 / math.pi) + " RawY: " + str(AccelValY)
                
            #
                
        def getSmoothAccelerometer(self):
            return self.smoothAccelX, self.smoothAccelY, self.smoothAccelZ
                
        def getGyro(self):
            gyro_xout = float(self.read_word_2c(0x43))
            gyro_yout = float(self.read_word_2c(0x45))
            gyro_zout = float(self.read_word_2c(0x47))
            return (gyro_xout * self.aclScale, gyro_yout * self.aclScale, gyro_zout * self.aclScale)

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
