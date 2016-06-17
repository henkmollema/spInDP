import time

from spInDP.Behavior import Behavior


class FuryRoadBehavior(Behavior):
    """Provides behavior which walks the fury road by following a line."""

    frameNr = 0

    def __init__(self, spider):
        """Initializes a new instance of the FuryRoadBehavior class."""
        super(FuryRoadBehavior, self).__init__(spider)

    def update(self):
		#Get sensor data
		leftSensorData, rightSensorData = self.spider.sensorDataProvider.readADC()
		
        if(leftSensorData >= 600)
			leftOnLine = True
		else
			leftOnLine = False
			
		if(rightSensorData >= 600)
			rightOnLine = True
		else
			rightOnLine = False

        if(leftOnLine and rightOnLine):
            #left and right on line, take a step forward
            execTime = self.spider.animationController.turnWalk(xDirection=0, yDirection=1, frameNr = self.frameNr)
        elif(not leftOnLine and not rightOnLine):
            #left and right not on line, probably in a turn
            self.frameNr -= 1 #Don't advance the frameNr and do nothing
            execTime = 0
        elif(leftOnLine):
            # only left is on line, turn right a little
            execTime = self.spider.animationController.turnWalk(xDirection=0.35, yDirection=1, frameNr=self.frameNr)
        elif(rightOnLine):
            #only right is on line, turn left a little
            execTime = self.spider.animationController.turnWalk(xDirection=-0.35, yDirection=1, frameNr=self.frameNr)

        time.sleep(execTime)
        self.frameNr += 1

        return
