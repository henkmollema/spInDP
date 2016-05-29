import time
import math
import json
from spInDP.ax12 import Ax12


class ServoController(object):
    """Provides interaction with the physical servos."""

    # Based on physical dimensions of scarJo
    femurLength = 11.0  # Femur length (cm)
    tibiaLength = 16.4  # Tibia (cm)
    coxaLength = 4.107  # Lengte coxa (cm)

    def __init__(self):
        self.ax12 = Ax12()

    def getPosition(self, servo):
        tryCount = 0
        maxTryCount = 3
        pos = None
        while pos == None and tryCount < maxTryCount:
            try:
                pos = self.ax12.readPosition(servo)
            except:
                print ("Error reading position from servo " + str(servo) + ". Retrying..")
                tryCount += 1
                continue
                
        return dxl_angle_to_degrees(pos)

    def getSpeed(self, servo):
        speed = self.ax12.readSpeed(servo)
        return speed

    def getTemperature(self, servo):
        temp = self.ax12.readTemperature(servo)
        return temp

    def getLoad(self, servo):
        load = self.ax12.readLoad(servo)
        return load

    def getVoltage(self, servo):
        volt = self.ax12.readVoltage(servo)
        return volt

    # Kinematics (non inverse) for leg positioning
    def setLegTorque(self, leg, status):
        for x in range ((int(leg)-1)*3+1, (int(leg)-1)*3+4):
            print ("Setting torque for servo " + str(x) + " from leg " + str(leg) + " to " + str(status))
            try:
                time.sleep(0.01)
                self.ax12.setTorqueStatus(x, int(status))
            except:
                #ignore error, but tell the user
                print ("Error setting servo + " + str(x) + " torque for leg " + str(leg))
                continue
    def setLegTorqueAll(self, status):
        for x in range(1, 19):
            print ("Setting torque for servo " + str(x) + " to " + str(status))
            try:
                self.ax12.setTorqueStatus(x, status)
            except:
                #ignore error and continue, but tell the user
                print ("Error setting servo torque for servo " + str(x))
                continue
    def computeKinematics(self, leg, legID):
        coxa = leg[1] * (math.pi/180)
        femur = (leg[2] + 90) * (math.pi/180)
        tibia = leg[3] * (math.pi/180)
        xOffset = 16.347
        zOffset = 5.59

        x = math.cos(coxa) * (self.coxaLength + (math.cos(femur) * self.femurLength) + (math.cos(femur - tibia) * self.tibiaLength)) - xOffset
        y = math.sin(coxa) * (self.coxaLength + (math.cos(femur) * self.femurLength) + (math.cos(femur - tibia) * self.tibiaLength))
        z = (math.sin(femur) * self.femurLength) + (math.sin(femur - tibia) * self.tibiaLength) - zOffset

        if (legID == 2 or legID == 3 or legID == 4):
            y *= -1

        return x,y,z

    def getAllLegsXYZ(self):
        legs = {}
        for legId in range(1, 7):
            legServos = {}
            for x in range(1, 4):
                servoId = (legId-1)*3+x
                legServos[x] = self.getPosition(servoId)
            try:
                legs[legId] = self.computeKinematics(legServos, legId)
            except:
                print ("Something went wrong in \"computeKinematics\"...")
                continue
        return legs

    # Generates a JSON string with data from all servos.
    def getServoDataJSON(self):
        retVal = {}
        for x in range(1, 19):
            try:
                tmp = {}
                retVal[x] = tmp
                tmp['position'] = self.getPosition(x)
                tmp['temp'] = self.getTemperature(x)
                tmp['load'] = self.getLoad(x)
                tmp['voltage'] = str(
                    float(float(self.getVoltage(x)) / float(10)))

            except:
                # Ignore errors with servos
                continue

        return json.dumps(retVal, separators=(',', ':'))

    def isMoving(self, servo):
        return self.ax12.readMovingStatus(servo) == 1

    def move(self, servo, angle, speed=200):
        pos = int(degrees_to_dxl_angle(angle))

        #print("moving: " + str(servo) + " to: " + str(angle) + ", pos: " + str(pos) + ", speed: " + str(speed))

        self.ax12.moveSpeed(servo, pos, int(speed))


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
