class LegMovement(object):
    """Represents a leg movement."""

    def __init__(self):
        """Initializes a new instance of the LegMovement class."""

        self.empty = False
        self.coxa = 0.0
        self.tibia = 0.0
        self.femur = 0.0
        self.coxaSpeed = 0.0
        self.tibiaSpeed = 0.0
        self.femurSpeed = 0.0
        self.maxExecTime = 0.0
        self.IKCoordinates = [0, 0, 0]
