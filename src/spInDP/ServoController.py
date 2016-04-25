from ax12 import Ax12
import time

class ServoController(object):
    """Provides interaction with the physical servos."""

    def __init__(self):
        self.ax12 = Ax12()

    def getData(self, servo):
        return -1

    def write(self, servo, angle):
        pos = angleToPosition(angle)
        self.ax12.move(servo, angle);
        #time.sleep(angle * 0.0004)

    def angleToPosition(angle):
        return 1024 * (abs(angle) / 360)

    def positionToAngle(position):
        return 360 * (abs(position) / 1024)
