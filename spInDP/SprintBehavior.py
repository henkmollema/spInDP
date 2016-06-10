import time

from spInDP.Behavior import Behavior


class SprintBehavior(Behavior):
    """Provides sprinting behavior using a sequence file."""

    def __init__(self, spider):
        """Initializes a new instance of the SprintBehavior class."""
        super(SprintBehavior, self).__init__(spider)

    def update(self):
        jY = self.spider.remoteController.context.jY
        if (jY < 0.3):
            x = self.spider.sequenceController.parseSequence("sequences/run.txt",
                                                             validate=False,
                                                             speedModifier=4,
                                                             repeat=1)
            time.sleep(x)
