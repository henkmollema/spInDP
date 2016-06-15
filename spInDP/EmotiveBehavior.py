import time

from spInDP.Behavior import Behavior


class EmotiveBehavior(Behavior):
    """Provides manual behavior of a spider using the RemoteContext."""
    emoContext = None
    frameNr = 0

    def __init__(self, spider):
        """Initializes a new instance of the ManualBehavior class."""

        super(EmotiveBehavior, self).__init__(spider)
        self.emoContext = spider.emotiveContext

    def update(self):
        command = self.emoContext.currentCommand
        #print command
        if(command != "s"):
            execTime = 0
            if(command == "f"):
                execTime = self.spider.animationController.walk(direction=0,
                                                                frameNr=self.frameNr,
                                                                speedMod=1,
                                                                keepLeveled=False) - self.spider.UPDATE_SLEEP_TIME

            elif(command == "l"):
                turnAngle = -1
                execTime = self.spider.animationController.turn(direction=turnAngle,
                                                                frameNr=self.frameNr,
                                                                speedMod=1,
                                                                keepLeveled=False) - self.spider.UPDATE_SLEEP_TIME

            elif(command == "r"):
                turnAngle = 1
                execTime = self.spider.animationController.turn(direction=turnAngle,
                                                                frameNr=self.frameNr,
                                                                speedMod=1,
                                                                keepLeveled=False) - self.spider.UPDATE_SLEEP_TIME

            time.sleep(max(execTime, 0))
            self.frameNr += 1

