from spInDP.Behavior import Behavior
import time
from spInDP.AnimationController import AnimationController


class PushBehavior(Behavior):

    frameNr = 1
    lastZ = 0
    animationController = None
    remoteContext = None

    def __init__(self, spider):
        print("Initializing spider gap.")
        super(PushBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.context
        self.animationController = AnimationController(spider)

    def update(self):
        jMagnitude = self.remoteContext.jMagnitude
        angleModifier = 1
        if(jMagnitude > 0.4):
            print("jMagnituge = ", jMagnitude)
            speedModifier = jMagnitude * 2

            time.sleep(self.animationController.push(frameNr=self.frameNr, speedMod=speedModifier))

            #self.animationController.push(frameNr=self.frameNr, speedMod=speedModifier)
            self.frameNr += 1
            print("hohihohohihohi")

        return
