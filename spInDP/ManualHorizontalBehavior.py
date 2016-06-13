from spInDP.ManualBehavior import ManualBehavior


class ManualHorizontalBehavior(ManualBehavior):
    """Provides manual behavior of a spider using the RemoteContext while keeping the body horizontal."""

    _super = None

    def __init__(self, spider):
        """Initializes a new instance of the SprintBehavior class."""

        print ("Initialize ManualHorizontalBehavior")
        self._super = super(ManualHorizontalBehavior, self)
        self._super.__init__(spider)
        self.keepLeveled = True

    def update(self):
        self._super.update()
