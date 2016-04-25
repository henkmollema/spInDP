import time
from pyax12.connection import Connection

class ServoController(object):
    """Provides interaction with the physical servos."""

    def __init__(self):
        self.connection = Connection("/dev/ttyAMA0", baudrate=1000000, timeout=0.5)

    #def getData(self, servo):
    #    return -1

    def move(self, servo, angle):
        self.connection.goto(servo, angle, speed=512, degrees=True)
        #time.sleep(angle * 0.0004)

    def getTemp(self, servo):
        return self.connection.get_present_temperature(servo)

    #def angleToPosition(angle):
    #    return 1024 * (abs(angle) / 300)

    #def positionToAngle(position):
    #    return 300 * (abs(position) / 1024)
