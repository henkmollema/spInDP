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
                time.sleep(self.spider.animationController.push(frameNr=self.frameNr, speedMod=speedModifier, direction=1))
            else:
                time.sleep(self.spider.animationController.push(frameNr=self.frameNr, speedMod=speedModifier, direction=0))
            self.frameNr += 1

        return
