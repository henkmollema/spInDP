import time
from pyax12.connection import Connection
import RPi.GPIO as GPIO
import math

class ServoController(object):
    """Provides interaction with the physical servos."""

    def __init__(self):
        self.connection = Connection("/dev/ttyAMA0", baudrate=1000000, timeout=0.5)

    def move(self, servo, angle, speed=200):        
        print("servo move " + str(servo) + ": " + str(angle))
        
        
        
        time.sleep(abs(angle) * 0.0033)

    def getTemp(self, servo):
        return self.connection.get_present_temperature(servo)
# TODO: improve the docstring
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