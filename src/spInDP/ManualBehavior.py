from Behavior import Behavior

class ManualBehavior(Behavior):
    """Represents the manual behavior of a spider"""

    def update(self):
       print("update from ManualBehavior")
