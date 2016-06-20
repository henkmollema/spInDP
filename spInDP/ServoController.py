# coding=utf-8
import time
import math
import json
from spInDP.ax12 import Ax12


class ServoController(object):
    """Provides interaction with the physical servos."""

    # Based on physical dimensions of scarJo
    FEMUR_LENGTH = 11.0  # Femur length (csm)
    TIBIA_LENGTH = 16.4  # Tibia (cm)
    COXA_LENGTH = 4.107  # Lengte coxa (cm)

    _torqueStatus = [1, 1, 1, 1, 1, 1]

    def __init__(self):
        """Initializes the ServoController class."""

        self.ax12 = Ax12()

    def getPosition(self, servo):
        """Gets the present position of the specified servo."""

        tryCount = 0
        maxTryCount = 3
        pos = -1
        while pos == -1 and tryCount < maxTryCount:
            try:
                pos = self.ax12.readPosition(servo)
            except:
                print ("Error reading position from servo " + str(servo) + ". Retrying..")
                tryCount += 1
                continue

        return dxlAngleToDegrees(pos)

    def getSpeed(self, servo):
        """Gets the present speed of the specified servo."""

        speed = self.ax12.readSpeed(servo)
        return speed

    def getTemperature(self, servo):
        """Gets the current temperature of the specified servo."""

        temp = self.ax12.readTemperature(servo)
        return temp

    def getLoad(self, servo):
        """Gets the present load of the specified servo."""

        load = self.ax12.readLoad(servo)
        return load

    def getVoltage(self, servo):
        """Gets the present voltage of the specified servo."""

        volts = self.ax12.readVoltage(servo)
        return volts

    def getLegTorque(self, leg):
        """Gets the torque on the specified leg."""

        return self._torqueStatus[leg - 1]

    def setComplianceMargin(self):
        """Sets the compliance margin on the all the servos."""

        for x in range(1, 19):
            tries = 0
            maxTries = 3
            while tries <= maxTries:
                try:
                    print ("set compliance of servo " + str(x))
                    self.ax12.setCompliance(x, 1, 1, 32, 32)
                    break
                except:
                    print ("compliance failed for servo " + str(x))
                    tries += 1

    # Kinematics (non inverse) for leg positioning
    def setLegTorque(self, leg, status):
        """Sets the torque status for the specified leg."""

        for x in range((int(leg) - 1) * 3 + 1, (int(leg) - 1) * 3 + 4):
            print ("Setting torque for servo " + str(x) + " from leg " + str(leg) + " to " + str(status))
            try:
                time.sleep(0.01)
                self.ax12.setTorqueStatus(x, int(status))
                self._torqueStatus[int(x / 3)] = status
            except:
                # ignore error, but tell the user
                print ("Error setting servo + " + str(x) + " torque for leg " + str(leg))
                continue

    def setLegTorqueAll(self, status):
        """Sets the torque status for all the legs."""

        for x in range(1, 19):
            print ("Setting torque for servo " + str(x) + " to " + str(status))
            try:
                self.ax12.setTorqueStatus(x, status)
                self._torqueStatus[int(x / 3)] = status
            except:
                # ignore error and continue, but tell the user
                print ("Error setting servo torque for servo " + str(x))
                continue

    def anglesToCoords(self, leg, legID):
        """Converts the angles of the specified leg servos to coords."""

        coxa = leg[1] * (math.pi / 180)
        femur = (leg[2] + 90) * (math.pi / 180)
        tibia = leg[3] * (math.pi / 180)
        xOffset = 16.347
        zOffset = 5.59

        x = math.cos(coxa) * (self.COXA_LENGTH + (math.cos(femur) * self.FEMUR_LENGTH) + (
            math.cos(femur - tibia) * self.TIBIA_LENGTH)) - xOffset
        y = math.sin(coxa) * (
            ServoController.COXA_LENGTH + (math.cos(femur) * ServoController.FEMUR_LENGTH) +
            (math.cos(femur - tibia) * ServoController.TIBIA_LENGTH))
        z = (math.sin(femur) * self.FEMUR_LENGTH) + (math.sin(femur - tibia) * self.TIBIA_LENGTH) - zOffset

        if legID == 2 or legID == 3 or legID == 4:
            y *= -1

        return round(x, 1), round(y, 1), round(z, 1)

    def getAllLegsXYZ(self):
        """Gets the X, Y, Z of all the legs."""

        legs = ["", "", "", "", "", ""]
        for legId in range(1, 7):
            legServos = {}
            for x in range(1, 4):
                servoId = (legId - 1) * 3 + x
                legServos[x] = self.getPosition(servoId)
            try:
                coords = self.anglesToCoords(legServos, legId)
                legs[legId] = str(coords[0]) + "," + str(coords[1]) + "," + str(coords[2])
            except:
                print ("Something went wrong in \"anglesToCoords\"...")
                raise()
                continue
        return ' '.join([str(x) for x in legs])

    def getServoDataJSON(self):
        """Returns a JSON string with data from all servos."""

        retVal = {}
        for x in range(1, 19):
            try:
                tmp = {}
                retVal[x] = tmp
                tmp['position'] = self.getPosition(x)
                tmp['temp'] = self.getTemperature(x)
                tmp['load'] = self.getLoad(x)
                tmp['voltage'] = str(float(float(self.getVoltage(x)) / float(10)))

            except:
                # Ignore errors with servos
                continue

        return json.dumps(retVal, separators=(',', ':'))

    def isMoving(self, servo):
        """Returns a value indicating whether the specified servo is moving."""

        return self.ax12.readMovingStatus(servo) == 1

    def move(self, servo, angle, speed=200):
        """Moves the specified servo to the specified angle using the specified speed."""

        pos = int(degreesToDxlAngle(angle))
        self.ax12.moveSpeed(servo, pos, int(speed))


def dxlAngleToDegrees(dxl_angle):
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


def degreesToDxlAngle(angle_degrees):
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
