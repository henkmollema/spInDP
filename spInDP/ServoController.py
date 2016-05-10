import time
import math
from spInDP.ax12 import Ax12

class ServoController(object):
    """Provides interaction with the physical servos."""

    def __init__(self):
        self.ax12 = Ax12()
        
    def getPosition(self, servo):
        pos = self.ax12.readPosition(servo)
        return dxl_angle_to_degrees(pos)
        
    def isMoving(self, servo):
        return self.ax12.readMovingStatus(servo) == 1

    def move(self, servo, angle, speed=200):
        pos = int(degrees_to_dxl_angle(angle))
        
        #print("moving: " + str(servo) + " to: " + str(angle) + ", pos: " + str(pos) + ", speed: " + str(speed))
        
        self.ax12.moveSpeed(servo, pos, speed)

    def getTemp(self, servo):
        return self.ax12.readTemperature(servo)
        
def dxl_angle_to_degrees(dxl_angle):
    """Normalize the given angle.

    PxAX-12 uses the position angle (-150.0°, +150.0°) range instead of the
    (0°, +300.0°) range defined in the Dynamixel official documentation because
    the former is easier to use (especially to make remarkable angles like
    right angles or 45° and 135° angles).

    :param int dxl_angle: an angle defined according to the Dynamixel internal
        notation, i.e. in the range (0, 1023) where:

        - 0 is a 150° clockwise angle;
        - 1023 is a 150° counter clockwise angle.

    :return: an angle defined in degrees in the range (-150.0°, +150.0°) where:

        - -150.0 is a 150° clockwise angle;
        - +150.0 is a 150° counter clockwise angle.

    :rtype: float.
    """
    angle_degrees = round(dxl_angle / 1023. * 300. - 150.0, 1)
    return angle_degrees

def degrees_to_dxl_angle(angle_degrees):
    """Normalize the given angle.

    PxAX-12 uses the position angle (-150.0°, +150.0°) range instead of the
    (0°, +300.0°) range defined in the Dynamixel official documentation because
    the former is easier to use (especially to make remarkable angles like
    right angles or 45° and 135° angles).

    :param float angle_degrees: an angle defined in degrees the range
        (-150.0°, +150.0°) where:

        - -150.0 is a 150° clockwise angle;
        - +150.0 is a 150° counter clockwise angle.

    :return: an angle defined according to the Dynamixel internal notation,
        i.e. in the range (0, 1023) where:

        - 0 is a 150° clockwise angle;
        - 1023 is a 150° counter clockwise angle.

    :rtype: int.
    """
    dxl_angle = math.floor((angle_degrees + 150.0) / 300. * 1023.)
    return dxl_angle