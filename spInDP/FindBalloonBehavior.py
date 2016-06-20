import math
import time

from spInDP.AutonomeBehavior import AutonomeBehavior


class FindBalloonBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon."""

    BLOB_SIZE = 200
    _frameNr = 0
    _stabPosition = False

    _lastX = 1

    def __init__(self, spider):
        """Initializes a new instance of the FindBalloonBehavior class."""

        super(FindBalloonBehavior, self).__init__(spider)

    def update(self):
        balloonFound, coords, size = self.spider.visioncontroller.FindBalloon()

        if balloonFound:
            # When the balloon blob is big enough, stab it
            if size >= FindBalloonBehavior.BLOB_SIZE:

                # Determine whether the balloon is left or right
                balloonIsLeft = self.spider.visioncontroller.getBalloonIsLeft()

                # Bring the spider in position before stabbing
                if not self._stabPosition:
                    print ("Move the spider into stab position. Left: " + str(balloonIsLeft))

                    if balloonIsLeft:
                        time.sleep(self.spider.sequenceController.parseSequence('sequences/pre-stab-left.txt', speedModifier=2))
                    else:
                        time.sleep(self.spider.sequenceController.parseSequence('sequences/pre-stab-right.txt', speedModifier=2))

                    self._stabPosition = True

                print("Steek 'm in z'n rug!")
                if balloonIsLeft:
                    time.sleep(self.spider.sequenceController.parseSequence('sequences/stab-left.txt'))
                else:
                    time.sleep(self.spider.sequenceController.parseSequence('sequences/stab-right.txt'))
            else:
                x = coords[0]
                # y = coords[1]
                a = 240
                b = x

                # Angle to balloon in degrees
                angle = math.atan(b / a) * (180 / math.pi)
                angle *= 1.5

                execTime = self.spider.animationController.turnWalk(xDirection=(b / a),
                                                                    yDirection=1.0,
                                                                    frameNr=self._frameNr,
                                                                    speedMod=2)

                time.sleep(execTime)
                self._frameNr += 1
                self._lastX = x

        else:
            if self._stabPosition:
                print ("Execute post stab")
                time.sleep(self.spider.sequenceController.parseSequence('sequences/post-stab.txt'))

            # print ("Balloon not found, turning")
            turnDir = 1
            if self._lastX < 0:
                turnDir = -1

            execTime = self.spider.animationController.turnWalk(xDirection=turnDir,
                                                                yDirection=0.0,
                                                                frameNr=self._frameNr,
                                                                speedMod=1,
                                                                stepSize=1.5)
            time.sleep(execTime)


            self._stabPosition = False
            self._frameNr += 1
