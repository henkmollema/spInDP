from Behavior import Behavior

class ManualBehavior(Behavior):
    """Provides manual behavior of a spider."""

    def __init__(self, remoteContext):
        self.remoteContext = remoteContext;

    def update(self):
        print("Update from ManualBehavior with context" + str(self.remoteContext))
