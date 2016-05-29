class IKArguments(object):

    def __init__(self):
        self.legID = 0
        self.speed = 0

        # The coordinates to move to
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        #The angles we are moving away from.
        self.coxaFrom = 0.0
        self.femurFrom = 0.0
        self.tibiaFrom = 0.0

