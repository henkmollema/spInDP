import math
import time

from spInDP.AutonomeBehavior import AutonomeBehavior


class FollowBalloonBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon."""

    CENTER_DEVIATION = 100
    BLOB_SIZE = 175
    _frameNr = 0
    _lastX = 1

    def __init__(self, spider):
        """Initializes a new instance of the FindBalloonBehavior class."""
        super(FollowBalloonBehavior, self).__init__(spider)

    def update(self):
        balloonFound, coords, size = self.spider.visioncontroller.FindBalloon()

        if balloonFound:
            if size >= FollowBalloonBehavior.BLOB_SIZE:
                # When the balloon blob is big enough, stab it
                print("Steek 'm in z'n rug!")

            else:
                x = coords[0]
                #y = coords[1]
                a = 240
                b = x

                # Angle to balloon in degrees
                angle = math.atan(b / a) * (180 / math.pi)
                angle *= 1.5

                execTime = self.spider.animationController.turnWalk(xDirection=(b / a),
                                                                    yDirection=1,
                                                                    frameNr=self._frameNr,
                                                                    speedMod=())

                time.sleep(execTime)
                self._frameNr += 1
                self._lastX = x

        else:
            #print ("Balloon not found, turning")
            turnDir = 1
            if self._lastX < 0:
                turnDir = -1

            execTime = self.spider.animationController.turnWalk(xDirection=turnDir,
                                                                yDirection=0,
                                                                frameNr=self._frameNr,
                                                                speedMod=2)
            time.sleep(execTime)

            self._frameNr += 1
