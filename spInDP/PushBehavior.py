from spInDP.Behavior import Behavior
import time
from spInDP.AnimationController import AnimationController


class PushBehavior(Behavior):
    
    frameNr = 1
    lastZ = 0
    animationController = None
    remoteContext = None

    def __init__(self, spider):
        print("Initializing push (spider gap) behavior.")
        super(PushBehavior, self).__init__(spider)

    def update(self):
        jMagnitude = self.spider.remoteController.context.jMagnitude
        angleModifier = 1
        if(jMagnitude > 0.4):
            speedModifier = jMagnitude * 2
            if self.spider.remoteController.context.jX > 0:
                time.sleep(self.spider.animationController.push(frameNr=self.frameNr, speedMod=speedModifier))
            else:
                time.sleep(self.spider.animationController.push(frameNr=self.frameNr, speedMod=speedModifier))
            self.frameNr += 1

        return

    def safeTransition(self):
        self.filled = False
        while(self.filled == False):
            try:
                self.currentLeg = self.spider.servoController.getAllLegsXYZ()
                self.filled = True
            except:
                print("can not get cords for legs.")



