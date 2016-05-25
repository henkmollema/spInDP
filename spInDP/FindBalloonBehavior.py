from spInDP.AutonomeBehavior import AutonomeBehavior
import time


class FindBalloonBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon"""

    centerDeviation = 100
    blobSizeArrive = 200

    def __init__(self, spider):
        super(FindBalloonBehavior, self).__init__(spider)

    stabPosition = False
    def update(self):
        balloonFound, coords, size = self.spider.visioncontroller.FindBalloon()

        if(balloonFound):
            if(abs(coords[0]) > self.centerDeviation):
                # Adjust horizontal
                if(coords[0] > 0):
                    print("Adjust to right")
                    self.spider.sequenceController.executeStepRight()
                    self.stabPosition = False
                else:
                    print("Adjust to left")
                    self.spider.sequenceController.executeStepLeft()
                    self.stabPosition = False
            else:
                # When the balloon is center screen
                if(size >= self.blobSizeArrive):
                    # When the balloon blob is big enough
                    print("!!! Steek 'm in z'n rug !!!")
                    
                    if (not self.stabPosition):
                        self.spider.sequenceController.executePreStabLeft()
                        self.stabPosition = True
                    
                    self.spider.sequenceController.executeStabLeft()
                else:
                    # If the balloon blob is not big enough, take a step
                    print("Step towards to balloon")
                    self.spider.sequenceController.executeStepForward()
                    self.stabPosition = False
