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
        pos = self.ax12.readPosition(servo)
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
        for x in range ((leg-1)*3+1, (leg-1)*3+4):
            print "Setting torque for servo " + str(x) + " from leg " + str(leg) + " to " + str(status)
            try:
                self.ax12.setTorqueStatus(x, status)
            except:
                #ignore error, but tell the user
                print "Error setting servo + " + str(x) + " torque for leg " + str(leg)
                continue
    def setLegTorqueAll(self, status):
        for x in range(1, 19):
            print "Setting torque for servo " + str(x) + " from leg " + str(leg) + " to " + str(status)
            try:
                self.ax12.setTorqueStatus(x, status)
            except:
                #ignore error and continue, but tell the user
                print "Error setting servo torque for servo " + str(x)
                continue
    def computeKinematics(self, leg):
        coxa = leg[1]
        femur = leg[2]
        tibia = leg[3]
        x = math.cos(coxa)*(coxaLength+(math.cos(femur)*femurLength)+(math.sin(math.pi-tibia-((math.pi/2)-femur))*tibiaLength))
        y = math.sin(coxa)*(coxaLength+math.cos(femur)*femurLength+math.sin(math.pi-tibia-((math.pi/2)-femur))*tibiaLength)
        z = (math.sin(femur)*femurLength)-(math.cos((math.pi-tibia-((math.pi/2)-femur)))*tibiaLength)
        legCoords = x,y,z
        return legCoords
    def getAllLegsXYZ(self):
        legs = {}
        for legId in range(1, 7):
            legServos = {}
            for x in range(1, 4):
                servoId = (legId-1)*3+x
                try:
                    legServos[x] = (self.getPosition(servoId)/180)*math.pi
                except:
                    # Ignore error
                    print "Error reading position from leg " + str(servoId)
                    continue
            legs[legId] = computeKinematics(legServos)
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
