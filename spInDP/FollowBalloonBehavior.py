from spInDP.AutonomeBehavior import AutonomeBehavior
import time
import math


class FollowBalloonBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon."""

    CENTER_DEVIATION = 100
    BLOB_SIZE = 200
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
                y = coords[1]
                a = 240
                b = x

                # Angle to balloon in degrees
                angle = math.atan(b / a) * (180 / math.pi)
                angle *= 1.5

                if(angle < 45):
                # Walk towards balloon
                    execTime = self.spider.animationController.walk(angle, frameNr=self._frameNr, speedMod=3)
                else:
                    turnDir = 1
                    if(x < 0):
                        turnDir = -1
                    execTime = self.spider.animationController.turn(turnDir, frameNr=self._frameNr, speedMod=2)


                time.sleep(execTime)
                self._frameNr += 1

                self._lastX = x

        else:
            print ("Balloon not found")
            turnDir = 1
            if(self._lastX < 0): turnDir = -1

            execTime = self.spider.animationController.turn(turnDir, frameNr=self._frameNr, speedMod=2)
            time.sleep(execTime)

            self._frameNr += 1
