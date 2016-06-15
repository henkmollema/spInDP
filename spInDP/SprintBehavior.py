import time

from spInDP.Behavior import Behavior


class SprintBehavior(Behavior):
    """Provides sprinting behavior using a sequence file."""

    frameNr = 0

    def __init__(self, spider):
        """Initializes a new instance of the SprintBehavior class."""

        super(SprintBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.context

    def update(self):
        jX = self.remoteContext.jX
        jY = self.remoteContext.jY
        jMagnitude = self.remoteContext.jMagnitude

        if jMagnitude > 0.2:
            speedModifier = jMagnitude * 2

            if self.spider.sequenceController.legQueueSize() < 2:
                execTime = self.spider.animationController.turnRun(xDirection=-jY,
                                                                   yDirection=-jX,
                                                                   frameNr=self.frameNr,
                                                                   speedMod=speedModifier)
                time.sleep(max(execTime, 0))

            self.frameNr += 1

    def restrict(self, val, minval, maxval):
        if val < minval:
            return minval
        elif val > maxval:
            return maxval

        return val
