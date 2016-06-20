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
        self.safeTransition()

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
        for x in [2,14,17]:
            self.spider.servoController.move(servo=x,angle=-10, speed=100)
        for x in [5,8,11]:
            self.spider.servoController.move(servo=x,angle=10, speed=100)