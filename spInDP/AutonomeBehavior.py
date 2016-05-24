from spInDP.Behavior import Behavior


class AutonomeBehavior(Behavior):
    """Provides autonome behavior of a spider"""
    
    def __init__(self, spider):
        super(AutonomeBehavior, self).__init__(spider)

    def update(self):
        print("Update from AutonomeBehavior")
