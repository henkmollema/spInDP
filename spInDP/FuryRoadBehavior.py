import time

from spInDP.Behavior import Behavior


class FuryRoadBehavior(Behavior):
    """Provides behavior which walks the fury road by following a line."""

    frameNr = 0
    _lastLeftOnLine = True
    _lastRightOnLine = True

    def __init__(self, spider):
        """Initializes a new instance of the FuryRoadBehavior class."""

        super(FuryRoadBehavior, self).__init__(spider)

        # Move the spider closer to the ground
        self.spider.animationController.zOffset = -2.7

    def update(self):
        # Get sensor data
        rightSensorData, leftSensorData = self.spider.sensorDataProvider.readADC()
        leftSensorData -= 60

        print("left: ", leftSensorData, "; right: ", rightSensorData)
        if (abs(leftSensorData - rightSensorData)) < 20:
            print("Its on line")
            leftOnLine = True
            rightOnLine = True
        elif leftSensorData >= 600 and rightSensorData >= 500:
            print ("Both not on line")
            leftOnLine = False
            rightOnLine = False
        elif leftSensorData < rightSensorData:
            print("Goto left")
            leftOnLine = True
            rightOnLine = False
        else:
            print("Goto right")
            leftOnLine = False
            rightOnLine = True

        execTime = 0
        if leftOnLine and rightOnLine:
            # left and right on line, take a step forward
            execTime = self.spider.animationController.turnWalk(xDirection=0,
                                                                yDirection=1,
                                                                frameNr=self.frameNr,
                                                                speedMod=1.5,
                                                                stepSize=1.5,
                                                                stepOffset=20)
        elif not leftOnLine and not rightOnLine:
            if self._lastRightOnLine:
                print ("Turn right")
                xDir = 1.0
            else:
                print ("Turn left")
                xDir = -1.0

            execTime = self.spider.animationController.turnWalk(xDirection=xDir,
                                                                yDirection=0,
                                                                frameNr=self.frameNr,
                                                                speedMod=1.5,
                                                                stepSize=1.5)

        elif leftOnLine:
            # only left is on line, turn right a little
            execTime = self.spider.animationController.turnWalk(xDirection=-1.0,
                                                                yDirection=0.5,
                                                                frameNr=self.frameNr,
                                                                speedMod=1.5,
                                                                stepSize=1.5)
        elif rightOnLine:
            # only right is on line, turn left a little
            execTime = self.spider.animationController.turnWalk(xDirection=1.0,
                                                                yDirection=0.5,
                                                                frameNr=self.frameNr,
                                                                speedMod=1.5,
                                                                stepSize=1.5)

        time.sleep(execTime)
        self.frameNr += 1
        self._lastLeftOnLine = leftOnLine
        self._lastRightOnLine = rightOnLine
