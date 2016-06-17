import time

from spInDP.Behavior import Behavior


class FuryRoadBehavior(Behavior):
    """Provides behavior which walks the fury road by following a line."""

    frameNr = 0

    def __init__(self, spider):
        """Initializes a new instance of the FuryRoadBehavior class."""

        super(FuryRoadBehavior, self).__init__(spider)
        self.spider.animationController.zOffset = -2.5

    def update(self):
        # Get sensor data
        rightSensorData, leftSensorData = self.spider.sensorDataProvider.readADC()
        leftSensorData -= 60

        print("left: ", leftSensorData, "; right: ", rightSensorData)
        #leftOnLine = True
        #rightOnLine = True
        if (abs(leftSensorData - rightSensorData)) < 20:
            print("Its on line")
            leftOnLine = True
            rightOnLine = True
        elif leftSensorData < rightSensorData:
            print("Goto left")
            leftOnLine = True
            rightOnLine = False
        else:
            print("Goto right")
            leftOnLine = False
            rightOnLine = True

        # if leftSensorData >= 600:
        #     leftOnLine = True
        # else:
        #     leftOnLine = False
        #
        # if rightSensorData >= 600:
        #     rightOnLine = True
        # else:
        #     rightOnLine = False

        execTime = 0
        if leftOnLine and rightOnLine:
            # left and right on line, take a step forward
            execTime = self.spider.animationController.turnWalk(xDirection=0, yDirection=1, frameNr=self.frameNr)
        elif not leftOnLine and not rightOnLine:
            # left and right not on line, probably in a turn
            self.frameNr -= 1  # Don't advance the frameNr and do nothing
            execTime = 0
        elif leftOnLine:
            # only left is on line, turn right a little
            execTime = self.spider.animationController.turnWalk(xDirection=-1.0, yDirection=1, frameNr=self.frameNr, speedMod=2.0)
        elif rightOnLine:
            # only right is on line, turn left a little
            execTime = self.spider.animationController.turnWalk(xDirection=1.0, yDirection=1, frameNr=self.frameNr, speedMod=2.0)

        time.sleep(execTime)
        self.frameNr += 1
