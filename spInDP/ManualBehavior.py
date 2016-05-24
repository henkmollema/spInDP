from spInDP.Behavior import Behavior


class ManualBehavior(Behavior):
    """Provides manual behavior of a spider."""

    def __init__(self, spider):
        super(ManualBehavior, self).__init__(spider)

    def update(self):
        return
