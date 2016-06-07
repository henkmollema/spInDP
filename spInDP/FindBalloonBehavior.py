from spInDP.AutonomeBehavior import AutonomeBehavior
import time
import math


class FindBalloonBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon."""

    CENTER_DEVIATION = 100
    BLOB_SIZE = 200
    _frameNr = 0
    _stabPosition = False

    def __init__(self, spider):
        """Initializes a new instance of the FindBalloonBehavior class."""

        super(FindBalloonBehavior, self).__init__(spider)

    def update(self):
        balloonFound, coords, size = self.spider.visioncontroller.FindBalloon()

        if balloonFound:
            if size >= FindBalloonBehavior.BLOB_SIZE:
                # When the balloon blob is big enough, stab it
                print("Steek 'm in z'n rug!")

                if not self._stabPosition:
                    self.spider.sequenceController.executePreStabLeft()
                    self._stabPosition = True

                self.spider.sequenceController.executeStabLeft()
            else:
                # if (self.stabPosition):
                #    print ("Execute post stab");
                #    self.spider.sequenceController.executePostStabLeft()

                x = coords[0]
                y = coords[1]
                a = 240
                b = x

                # Angle to balloon in degrees
                angle = math.atan(b / a) * (180 / math.pi)
                angle *= 1.5

                # Walk towards balloon
                execTime = self.spider.animationController.walk(angle, frameNr=self._frameNr, speedMod=1.5)
                time.sleep(execTime)
                self._stabPosition = False
                self._frameNr += 1
                # else:
                # print "Balloon not found"
                # execTime = self.spider.animationController.turn(20, frameNr=self.frameNr, speedMod=1)
                # time.sleep(execTime)
                # self.stabPosition = False
                # self.frameNr += 1
