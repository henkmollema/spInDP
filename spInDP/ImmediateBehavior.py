import math

from spInDP.AutonomeBehavior import AutonomeBehavior
from spInDP.SequenceFrame import SequenceFrame


class ImmediateBehavior(AutonomeBehavior):
    """Provides immediate behavior as it executes commands directly."""

    # An array of IKCoordinates
    _basePose = [[-7, -8, 5], [-7, -8, 5], [-5, 0, 5], [-7, 8, 5], [-7, 8, 5], [-5, 0, 5]]
    _currentPose = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    _remoteContext = None

    # Physical dimensions
    BODY_TO_SENSOR_MID = 0  # from mid body to mid coxas X
    BODY_TO_SENSOR = 12.05  # from mid body to back and front coxas X
    BODY_TO_SIDE = 10.45 + 16.347  # from mid body to side leg coxa Y

    def __init__(self, spider):
        """Initializes a new instance of the ImmediateBehavior class."""

        super(ImmediateBehavior, self).__init__(spider)
        self._remoteContext = self.spider.remoteController.context

    def update(self):
        """
        Manipulate the currentpose based on input or sensors
        Please note only the z coordinate can be safely modified
        when manipulating the x or y coordinate make sure the leg
        is in the air.
        """

        yAngle = 0
        xAngle = 0

        yAngle = self._remoteContext.aY * 30 * math.pi / 180
        xAngle = self._remoteContext.aX * 30 * math.pi / 180

        for x in range(1, 7):
            newIKCoordinates = list(self._basePose[x - 1])  # copy the basePose

            # Change the z-coordinate based on joystick position and legID
            if (x == 1 or x == 2):  # front legs
                newIKCoordinates[2] += math.sin(yAngle) * (
                    ImmediateBehavior.BODY_TO_SENSOR - self._basePose[x - 1][1]) / 2
                if x == 1:
                    newIKCoordinates[2] -= math.sin(xAngle) * (
                        ImmediateBehavior.BODY_TO_SIDE + self._basePose[x - 1][0]) / 2
                if x == 2:
                    newIKCoordinates[2] += math.sin(xAngle) * (
                        ImmediateBehavior.BODY_TO_SIDE + self._basePose[x - 1][0]) / 2
            elif (x == 4 or x == 5):  # back legs
                newIKCoordinates[2] += math.sin(yAngle) * -(
                    ImmediateBehavior.BODY_TO_SENSOR + self._basePose[x - 1][1]) / 2
                if x == 5:
                    newIKCoordinates[2] += math.sin(xAngle) * -(
                        ImmediateBehavior.BODY_TO_SIDE + self._basePose[x - 1][0]) / 2
                if x == 4:
                    newIKCoordinates[2] += math.sin(xAngle) * (
                        ImmediateBehavior.BODY_TO_SIDE + self._basePose[x - 1][0]) / 2
            else:  # side legs
                newIKCoordinates[2] += math.sin(yAngle) * (self._basePose[x - 1][1]) / 2
                if x == 6:
                    newIKCoordinates[2] += math.sin(xAngle) * -(
                        ImmediateBehavior.BODY_TO_SIDE + self._basePose[x - 1][0]) / 2
                if x == 3:
                    newIKCoordinates[2] += math.sin(xAngle) * (
                        ImmediateBehavior.BODY_TO_SIDE + self._basePose[x - 1][0]) / 2

            self._currentPose[x - 1] = newIKCoordinates

        # Set the servos to the currentpose with speed 150
        newFrame = self.poseToSequenceFrame(self._currentPose, 75)
        self.spider.sequenceController.setFrame(newFrame)

    def poseToSequenceFrame(self, pose, speed):
        """Returns a sequence frame for the specified pose with the specified speed."""

        seqFrame = SequenceFrame()
        for x in range(0, 6):
            seqFrame.movements[x + 1] = self.spider.sequenceController.coordsToLegMovement(pose[x][0], pose[x][1],
                                                                                           pose[x][2], x + 1, speed,
                                                                                           immediateMode=True)

        return seqFrame
