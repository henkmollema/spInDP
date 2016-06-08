from spInDP.Behavior import Behavior
import time
from spInDP.AnimationController import AnimationController


class PushBehavior(Behavior):

    frameNr = 0
    lastZ = 0
    animationController = None

    def __init__(self, spider):
        print("Initializing spider gap.")
        super(PushBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.context
        self.animationController = AnimationController(spider)

    def update(self):
        for x in range(1, 6):
            execTime = self.animationController.push(self.frameNr, 1)
            time.sleep(execTime)
            self.frameNr += 1

    def update2(self):
        jMagnitude = self.remoteContext.jMagnitude

        if (jMagnitude > 0.4):
            speedModifier = jMagnitude * 2

            time.sleep(max(self.animationController.push(frameNr = self.frameNr, speedMod = speedModifier)))
            self.frameNr += 1
        return
