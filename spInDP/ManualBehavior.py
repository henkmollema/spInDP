from spInDP.Behavior import Behavior
import math
import time


class ManualBehavior(Behavior):
    """Provides manual behavior of a spider."""
    frameNr = 0

    def __init__(self, spider):
        super(ManualBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.Context

    def update(self):
        jX = self.remoteContext.jX
        jY = self.remoteContext.jY
        jZ = self.remoteContext.jZ
                
        cJX = float((jX - 512.0) / 512.0)
        cJY = float(-(jY - 512.0) / 512.0)
        cJZ = float(self.remoteContext.jZ)
        
        angle = math.atan2(cJY, cJX) * (180/math.pi) - 90
        magnitute = math.sqrt((cJX**2) + (cJY**2))
        magnitute = self.restrict(magnitute, 0, 1)
        
        #print "Joystick = X: " + str(cJX) + ", Y: " + str(cJY) + ", Z: " + str(cJZ) + " magnitude: " + str(magnitute)
           
        #print "mag: " + str(magnitute)
        if(magnitute > 0.4):
            magnitute *= 2

            if(cJZ == 0): #strafemode
                kut = "python"
                time.sleep(self.spider.animationController.walk(direction = angle, frameNr = self.frameNr, speedMod = magnitute) - self.spider.updateSleepTime)
            else:
                angle = self.restrict(angle, -30, 30)
                time.sleep(self.spider.animationController.turn(direction = angle, frameNr = self.frameNr, speedMod = magnitute) - self.spider.updateSleepTime)
                
                
            self.frameNr += 1
        
        return
        
    def restrict (self,val, minval, maxval):
        if val < minval: return minval
        if val > maxval: return maxval
        return val