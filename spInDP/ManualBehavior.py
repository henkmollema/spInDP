from spInDP.Behavior import Behavior
import math
import time


class ManualBehavior(Behavior):
    """Provides manual behavior of a spider."""
    frameNr = 0

    def __init__(self, spider):
        super(ManualBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.context

    def update(self):
        jX = self.remoteContext.jX
        jY = self.remoteContext.jY
        jZ = self.remoteContext.jZ
        jAngle = self.remoteContext.jAngle
        jMagnitude = self.remoteContext.jMagnitude
        
        #print "Joystick = X: " + str(jX) + ", Y: " + str(jY) + ", Z: " + str(jZ) + " magnitude: " + str(magnitute) + " angle: " + str(angle)
   
        #DEBUG
        #print "GYRO Y: " + str(((float(self.spider.sensorDataProvider.getAccelerometer()[1]) / 1000.0) / 16.0) * 90.0)
        #time.sleep(self.spider.animationController.walk(direction = 0, frameNr = 0, speedMod = 0.5, keepLeveled = True))
        #self.frameNr += 1
        #print "GYRO ANGLES: " + str(self.spider.sensorDataProvider.getAccelerometer()[0]) + ", " + str(self.spider.sensorDataProvider.getAccelerometer()[1]) + ", " + str(self.spider.sensorDataProvider.getAccelerometer()[2])
        #DEBUG
        self.spider.sensorDataProvider.startMeasuring()

        if(jMagnitude > 0.4):
            speedModifier = jMagnitude * 2

            if(jZ == 0): #strafemode
                time.sleep(max(self.spider.animationController.walk(direction = jAngle, frameNr = self.frameNr, speedMod = jMagnitude) - self.spider.updateSleepTime, 0))
            else:
                turnAngle = self.restrict(jAngle, -30, 30)
                time.sleep(max(self.spider.animationController.turn(direction = turnAngle, frameNr = self.frameNr, speedMod = jMagnitude) - self.spider.updateSleepTime, 0))
                
            self.frameNr += 1
        return
        
    def restrict (self,val, minval, maxval):
        if val < minval: return minval
        if val > maxval: return maxval
        return val