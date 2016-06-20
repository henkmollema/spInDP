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

    def update(self):
        #get vision line data
        foundLine, lineCoords = self.spider.visioncontroller.getLine()
        lineXcoord = lineCoords[0]

        xDirection = lineXcoord
        yDirection = 1
        if abs(lineXcoord) > 80:
            yDirection = 1 - (lineXcoord - 80)
            if yDirection < 0:
                yDirection = 0

        execTime = self.spider.animationController.turnWalk(xDirection=xDirection,
                                                            yDirection=yDirection,
                                                            frameNr=self.frameNr,
                                                            speedMod=1.5,
                                                            stepSize=1.5)

        """
        print("Vision line data x coord: " + str(lineXcoord) + " foundLine: " + str(foundLine))
        if  foundLine and lineXcoord >= -80 and lineXcoord <= 80:
            print("Its on line")
            leftOnLine = True
            rightOnLine = True
        elif not foundLine:
            print ("Both not on line")
            leftOnLine = False
            rightOnLine = False
        elif lineXcoord < -80:
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
                                                                stepSize=1.5)
        elif not leftOnLine and not rightOnLine:
            if self._lastRightOnLine:
                print ("Turn right")
                xDir = 1.0
            else:
                print ("Turn left")
                xDir = -1.0

            print "both not on line xdir: " + str(xDir)
            execTime = self.spider.animationController.turnWalk(xDirection=xDir,
                                                                yDirection=0,
                                                                frameNr=self.frameNr,
                                                                speedMod=1.5,
                                                                stepSize=1.5)

        elif leftOnLine:

            print "leftOnline"
            # only left is on line, turn right a little
            execTime = self.spider.animationController.turnWalk(xDirection=-1.0,
                                                                yDirection=0.5,
                                                                frameNr=self.frameNr,
                                                                speedMod=1.5,
                                                                stepSize=1.5)
        elif rightOnLine:
            print "rightOnline"
            # only right is on line, turn left a little
            execTime = self.spider.animationController.turnWalk(xDirection=1.0,
                                                                yDirection=0.5,
                                                                frameNr=self.frameNr,
                                                                speedMod=1.5,
                                                                stepSize=1.5)
        """

        time.sleep(execTime)
        self.frameNr += 1

        """
        if(foundLine):
            self._lastLeftOnLine = leftOnLine
            self._lastRightOnLine = rightOnLine
        """
