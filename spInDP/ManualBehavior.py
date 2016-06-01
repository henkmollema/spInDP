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
        jX = int(self.remoteContext.jX)
        jY = int(self.remoteContext.jY)
        jZ = int(self.remoteContext.jZ)
        
        #print ("Updateloop: Joystick = X: " + str(jX) + ", Y: " + str(jY) + ", Z: " + str(jZ))
        
        cJX = -(jX - 512) / 512
        cJY = -(jY - 512) / 512
        cJZ = self.remoteContext.jZ
        
        if(jX > -0.2 and jX < 0.2):
            cJX = 0
            
        if(jY > -0.2 and jY < 0.2):
            cJY = 0
            
        if(cJX is not 0 or cJY is not 0):
        
            angle = math.atan2(cJY, cJX) * (180/math.pi) - 90
            magnitute = math.sqrt(cJX**2 + cJY**2)
            
            if(cJZ == 0): #strafemode
                time.sleep(self.spider.animationController.walk(direction = angle, frameNr = self.frameNr, speedMod = magnitute))
            else: #turnmode
                angle = self.restrict(angle, -30, 30)
                #print ("turn: " + str(angle))
                self.spider.animationController.turn(amountDegrees = angle, frameNr = self.frameNr, speedMod = magnitute)
                
            self.frameNr += 1
        
        return
        
    def restrict (self,val, minval, maxval):
        if val < minval: return minval
        if val > maxval: return maxval
        return val