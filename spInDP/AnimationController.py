import math
from spInDP.LegMovement import LegMovement
from spInDP.SequenceFrame import SequenceFrame

class AnimationController:
    """"Provides dynamic animations"""
    #Leg z coordinates
    legAirHigh = 0
    legAir = 2
    legGround = 5

    #Coordinates for the legs when walking normally
    legWideMid = {
        1: [-7, -8],
        2: [-7, -8],
        3: [-7, 0],
        4: [-7, 8],
        5: [-7, 8],
        6: [-7, 0]
    }

    #Coordinates for the legs when walking narrowly
    legNarrowMid = {
        1: [-5, -1],
        2: [-5, -1],
        3: [-5, 0], #Dont change the Y axis
        4: [-5, 1], #Don't change the Y axis
        5: [-5, 1],
        6: [-5, 0]
    }

    #Coordinates for the legs when walking over the spidergap
    legSpiderGap = {
        1: [-4, -8],
        2: [-4, -8],
        3: [0, 0],
        4: [-4, 8],
        5: [-4, 8],
        6: [0, 0]
    }

    #Coordinates for the legs when running
    legRunMid = {
        1: [-4.347,-9.265],
        2: [-4.347,-9.265],
        3: [-4.347,0],
        4: [-4.347,9.265],
        5: [-4.347,9.265],
        6: [-4.347,0]
    }

    shouldSafeTransition = False

    wideWalking = True
    highWalking = False
    zOffset     = 0

    turnInfo = None
    turnWalkInfo = None

    sideLegDistanceFromCenter = 10.45 #From the middle of the body to the turning point of the coxa of a sideleg
    cornerLegDistanceFromCenter = 13.845 #From the middle of the body to the turning point of the coxa of a cornerleg
    stockLegLength = 16.347 #the topdown length of the leg at coords 0,0,0
    stockCornerCoxaAngle = 119.5 #angle in the body middle with a line from leg-3-coxa to leg-1-coxa going through the middle

    cornerCoxaYDistanceFromCenter = 12.05 #Distance from the coxa of one of the corner legs to the middle of the body without the X axis (a vertical line from top to middle)
    cornerCoxaXDistanceFromCenter = 6.818 #Distance from the coxa of one of the cornes legs to the middle of the body without the Y axis (a horizontal line from left to middle)
    leg3ToLeg1Distance = 21.056 #Distance between coxa turnpoints
    midToLeg3ToLeg1Angle = 34.91 #Angle of the line from 'Body mid' > leg3 coxa > leg1 coxa at leg3 coxa

    seqCtrl = None
    yAdjustment = 0 #Y rotation for the current adjustment. (used in keeping the body upright)
    
    bodytoSensorMid = 0 # from mid body to mid coxas X-axis
    bodytoSensor = 12.05 # from mid body to back and front coxas X-axis

    def __init__(self, spider):
        self.spider = spider
        self.seqCtrl = spider.sequenceController

    """
        destination is a SequenceFrame object
    """
    def safeTransitionTo(self, destination, speed = 200):
        cLegCoords = []
        cDestCoords = []
        retVal = 0

        self.shouldSafeTransition = False

        for x in range(1,7):
            cLegCoords.append(self.spider.sequenceController.getLegCoords(x))
            if(destination.movements.get(x, None) is not None):
                cDestCoords.append(destination.movements[x].IKCoordinates)

            else:
                cDestCoords.append(self.spider.sequenceController.getLegCoords(x))

        #zSortedLegCoords = sorted(cLegCoords, key=lambda obj: obj[2])
        zSortedDestCoords = sorted(cDestCoords, key=lambda obj: obj[2])
        cGroundCoord  = zSortedDestCoords[5][2]
        #cGroundCoord = max(cGroundCoord, zSortedDestCoords[5][2])

        # set all legs to cGroundCoord
        self.startFrame()
        for x in range(1, 7):
            self.sequenceFrame.movements[x] = self.seqCtrl.coordsToLegMovement(cLegCoords[x-1][0], cLegCoords[x-1][1], cGroundCoord, x, speed)
        retVal += self.endFrame()

        #after that, one by one, elevate the legs a little and send them to their destination
        for legID in range(1,7):
            destCoords = cDestCoords[legID - 1]

            #Elevate this leg
            self.startFrame()
            self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(cLegCoords[x-1][0], cLegCoords[x-1][1], cGroundCoord - 3, legID, speed)
            retVal += self.endFrame()

            #Send this leg to the destination
            self.startFrame()
            self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(destCoords[0], destCoords[1], destCoords[2], legID, speed)
            retVal += self.endFrame()

        return retVal


    def setWideWalking(self, value):
        """Adjust midpoint of each leg, mainly to fit through 'het poortje'"""
        self.wideWalking = value
        self.shouldSafeTransition = True

    def setHighWalking(self, value):
        """Adjust the height of the legs when they are airborne"""
        self.highWalking = value
        if(value):
            self.setWideWalking(True)

    def startFrame(self):
        self.sequenceFrame = SequenceFrame()

    def endFrame(self):
        """Adds the frame to the queue and returns the time the execution will take"""
        #Add the new frame to the leg queues
        if(not self.shouldSafeTransition):
            self.seqCtrl.addFrameToQueue(self.sequenceFrame)

            ret = self.sequenceFrame.maxMaxExecTime
            self.sequenceFrame.movements = {}  # Clear the frame
            self.sequenceFrame = None
        else:
            tmpMovements = dict(self.sequenceFrame.movements)
            tmpFrame = SequenceFrame()
            tmpFrame.movements = tmpMovements

            self.sequenceFrame.movements = {}  # Clear the frame
            self.sequenceFrame = None

            ret = self.safeTransitionTo(tmpFrame)

        return ret

    def turnWalk(self, xDirection, yDirection, frameNr, speedMod=1):
        if xDirection < -1:
            xDirection = -1
            print("xDirection in turnWalk can't be lower than -1. It was modified from " + str(xDirection) + " to -1")
        if xDirection > 1:
            xDirection = 1
            print("xDirection in turnWalk can't be higher than 1. It was modified from " + str(xDirection) + " to 1")
        if yDirection < -1:
            yDirection = -1
            print("yDirection in turnWalk can't be lower than -1. It was modified from " + str(yDirection) + " to -1")
        if yDirection > 1:
            yDirection = 1
            print("yDirection in turnWalk can't be higher than 1. It was modified from " + str(yDirection) + " to 1")

        xDirection = round(xDirection, 2)
        yDirection = round(yDirection, 2)

        midXOffset = 0
        if xDirection == 0:
            midXOffset = 10000000
        elif yDirection == 0:
            midXOffset = 0
        else:
            midXOffset = 100 * abs(yDirection) * (1 / xDirection)

        stepSizeCm = 3.5

        legMid = {}
        if self.wideWalking:
            legMid = self.legWideMid
        else:
            legMid = self.legNarrowMid

        zGround = self.legGround
        zAir = self.legAir

        turnWalkInfo = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
        highestTotalDistance = 0
        for x in range(1, 7):
            legDistanceFromCenter = 0.0  # 6
            if x == 6:  # left mid
                legDistanceFromCenter = 10.45 + midXOffset
            elif x == 3:  # right mid
                legDistanceFromCenter = 10.45 - midXOffset
            elif x == 1 or x == 5:  # left corners
                legDistanceFromCenter = math.sqrt((self.cornerCoxaXDistanceFromCenter + midXOffset) ** 2 + self.cornerCoxaYDistanceFromCenter ** 2)
            elif x == 2 or x == 4:  # right corners
                legDistanceFromCenter = math.sqrt((self.cornerCoxaXDistanceFromCenter - midXOffset) ** 2 + self.cornerCoxaYDistanceFromCenter ** 2)

            legLength = math.sqrt((self.stockLegLength + legMid[x][0]) ** 2 + legMid[x][1] ** 2)
            positionDifference = math.sqrt(legMid[x][0] ** 2 + legMid[x][1] ** 2)
            extraCoxaAngle = math.acos((legLength ** 2 + self.stockLegLength ** 2 - positionDifference ** 2) / (2 * legLength * self.stockLegLength)) / math.pi * 180
            coxaAngle = 0
            if x == 1 or x == 5:
                if midXOffset < -self.cornerCoxaYDistanceFromCenter:
                    coxaAngle = 90 - math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4
                else:
                    coxaAngle = 90 + math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4
            elif x == 2 or x == 4:
                if midXOffset < self.cornerCoxaYDistanceFromCenter:
                    coxaAngle = 90 + math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4
                else:
                    coxaAngle = 90 - math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4

            actualCoxaAngle = coxaAngle + extraCoxaAngle

            totalDistance = 0
            if x == 3 or x == 6:
                totalDistance = abs(legDistanceFromCenter + legLength)
            else:
                totalDistance = math.sqrt(legDistanceFromCenter ** 2 + legLength ** 2 - 2 * legDistanceFromCenter * legLength * math.cos(actualCoxaAngle * math.pi / 180))

            if totalDistance > highestTotalDistance:
                highestTotalDistance = totalDistance

            angleFromCenter = 0
            if x == 3:
                if midXOffset < self.sideLegDistanceFromCenter:
                    angleFromCenter = 0
                else:
                    angleFromCenter = 180
            elif x == 6:
                if midXOffset < -self.sideLegDistanceFromCenter:
                    angleFromCenter = 180
                else:
                    angleFromCenter = 0
            else:
                angleFromCenter1 = coxaAngle
                angleFromCenter2 = math.acos((totalDistance ** 2 + legDistanceFromCenter ** 2 - legLength ** 2) / (2 * totalDistance * legDistanceFromCenter)) / math.pi * 180
                angleFromCenter = angleFromCenter1 + angleFromCenter2

            angleCompensatorX = totalDistance * math.cos(angleFromCenter * math.pi / 180) - totalDistance
            angleCompensatorY = totalDistance * math.sin(angleFromCenter * math.pi / 180) - totalDistance

            turnWalkInfo[x]["totalDistance"] = totalDistance
            turnWalkInfo[x]["angleFromCenter"] = angleFromCenter
            turnWalkInfo[x]["angleCompensatorX"] = angleCompensatorX
            turnWalkInfo[x]["angleCompensatorY"] = angleCompensatorY

        subCorner = math.acos((highestTotalDistance ** 2 + stepSizeCm ** 2 - highestTotalDistance ** 2) / (2 * highestTotalDistance * stepSizeCm)) / math.pi * 180
        stepSizeDegrees = 180 - (subCorner * 2)
        if (yDirection == -1) ^ (xDirection < 0):
            stepSizeDegrees *= -1

        frameNr = frameNr % 6

        leg36FrameNr = (frameNr - 2) % 6
        leg25FrameNr = frameNr
        leg14FrameNr = (frameNr - 4) % 6
        self.startFrame()
        if leg36FrameNr == 5:
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(legMid[3][0], legMid[3][1], zAir, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(legMid[6][0], legMid[6][1], zAir, 6, speedMod * 200)
        else:
            x = legMid[3][0] + (turnWalkInfo[3]["totalDistance"] * math.cos((turnWalkInfo[3]["angleFromCenter"] - (2 - leg36FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[3]["totalDistance"] - turnWalkInfo[3]["angleCompensatorX"])
            y = legMid[3][1] - (turnWalkInfo[3]["totalDistance"] * math.sin((turnWalkInfo[3]["angleFromCenter"] - (2 - leg36FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[3]["totalDistance"] - turnWalkInfo[3]["angleCompensatorY"])
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(x, y, zGround, 3, speedMod * 200 if leg36FrameNr == 0 else speedMod * 100)
            x = legMid[6][0] - (turnWalkInfo[6]["totalDistance"] * math.cos((turnWalkInfo[6]["angleFromCenter"] - (2 - leg36FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[6]["totalDistance"] - turnWalkInfo[6]["angleCompensatorX"])
            y = legMid[6][1] + (turnWalkInfo[6]["totalDistance"] * math.sin((turnWalkInfo[6]["angleFromCenter"] - (2 - leg36FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[6]["totalDistance"] - turnWalkInfo[6]["angleCompensatorY"])
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(x, y, zGround, 6, speedMod * 200 if leg36FrameNr == 0 else speedMod * 100)
        if leg25FrameNr == 5:
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(legMid[2][0], legMid[2][1], zAir, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(legMid[5][0], legMid[5][1], zAir, 5, speedMod * 200)
        else:
            x = legMid[2][0] + (turnWalkInfo[2]["totalDistance"] * math.cos((turnWalkInfo[2]["angleFromCenter"] - (2 - leg25FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[2]["totalDistance"] - turnWalkInfo[2]["angleCompensatorX"])
            y = legMid[2][1] + (turnWalkInfo[2]["totalDistance"] * math.sin((turnWalkInfo[2]["angleFromCenter"] - (2 - leg25FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[2]["totalDistance"] - turnWalkInfo[2]["angleCompensatorY"])
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(x, y, zGround, 2, speedMod * 200 if leg25FrameNr == 0 else speedMod * 100)
            x = legMid[5][0] + (turnWalkInfo[5]["totalDistance"] * math.cos((turnWalkInfo[5]["angleFromCenter"] - (2 - leg25FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[5]["totalDistance"] - turnWalkInfo[5]["angleCompensatorX"])
            y = legMid[5][1] - (turnWalkInfo[5]["totalDistance"] * math.sin((turnWalkInfo[5]["angleFromCenter"] - (2 - leg25FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[5]["totalDistance"] - turnWalkInfo[5]["angleCompensatorY"])
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(x, y, zGround, 5, speedMod * 200 if leg25FrameNr == 0 else speedMod * 100)
        if leg14FrameNr == 5:
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(legMid[1][0], legMid[1][1], zAir, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(legMid[4][0], legMid[4][1], zAir, 4, speedMod * 200)
        else:
            x = legMid[1][0] - (turnWalkInfo[1]["totalDistance"] * math.cos((turnWalkInfo[1]["angleFromCenter"] - (2 - leg14FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[1]["totalDistance"] - turnWalkInfo[1]["angleCompensatorX"])
            y = legMid[1][1] - (turnWalkInfo[1]["totalDistance"] * math.sin((turnWalkInfo[1]["angleFromCenter"] - (2 - leg14FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[1]["totalDistance"] - turnWalkInfo[1]["angleCompensatorY"])
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(x, y, zGround, 1, speedMod * 200 if leg14FrameNr == 0 else speedMod * 100)
            x = legMid[4][0] - (turnWalkInfo[4]["totalDistance"] * math.cos((turnWalkInfo[4]["angleFromCenter"] - (2 - leg14FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[4]["totalDistance"] - turnWalkInfo[4]["angleCompensatorX"])
            y = legMid[4][1] + (turnWalkInfo[4]["totalDistance"] * math.sin((turnWalkInfo[4]["angleFromCenter"] - (2 - leg14FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[4]["totalDistance"] - turnWalkInfo[4]["angleCompensatorY"])
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(x, y, zGround, 4, speedMod * 200 if leg14FrameNr == 0 else speedMod * 100)
        return self.endFrame()

    realYAngle = 0
    yAdjustment = 0
    def strafeWalk(self, direction, frameNr, speedMod = 1, keepLeveled = False):
        """Combination of walking and strafing, wherein the direction is an angle in degrees to which the body should move"""
        totalTime = 0

        cosDirection = math.cos(int(direction)*math.pi/180)
        sinDirection = math.sin(int(direction)*math.pi/180)

        legMid = {}
        stepRangeVert = 0.0
        stepRangeHor = 0.0
        zGround = 0 #When not using keepLeveled
        zAir = 0 #When not using keepLeveled
        if self.highWalking and self.wideWalking:
            legMid = self.legWideMid
            stepRangeVert = cosDirection * 14 #14 is stepsize for vertical walking
            stepRangeHor = sinDirection * 8 #8 is stepsize for horizontal walking
            zGround = self.legGround + self.zOffset
            zAir = self.legAirHigh + self.zOffset
        elif self.wideWalking:
            legMid = self.legWideMid
            stepRangeVert = cosDirection * 14 #14 is stepsize for vertical walking
            stepRangeHor = sinDirection * 8 #8 is stepsize for horizontal walking
            zGround = self.legGround + self.zOffset
            zAir = self.legAir + self.zOffset
        else:
            legMid = self.legNarrowMid
            stepRangeVert = cosDirection * 7 #7 is stepsize for vertical walking
            stepRangeHor = sinDirection * 7 #7 is stepsize for horizontal walking
            zGround = self.legGround - 2 + self.zOffset
            zAir = self.legAir + self.zOffset

        if(keepLeveled):
            zGround = 7 + self.zOffset
            zAir = 5 + self.zOffset

            cAccelY = float(self.spider.sensorDataProvider.getSmoothAccelerometer()[1] * math.pi / 180)
            self.realYAngle = self.spider.remoteController.context.accelY

        else:
            #Stop measuring accel
            self.spider.sensorDataProvider.stopMeasuring()

        zGround1 = zGround
        zGround2 = zGround
        zGround3 = zGround
        zGround4 = zGround
        zGround5 = zGround
        zGround6 = zGround
        zAir1 = zAir
        zAir2 = zAir
        zAir3 = zAir
        zAir4 = zAir
        zAir5 = zAir
        zAir6 = zAir

        frameNr = frameNr % 6
        if frameNr == 0:
            if(keepLeveled):
                zGround3 = -math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legMid[3][1] + (stepRangeVert / 2))) / 2 + zGround
                zGround6 = -math.sin(self.realYAngle) * (self.bodytoSensorMid + (legMid[6][1] + (stepRangeVert / 2))) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legMid[2][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legMid[5][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - (legMid[1][1])) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legMid[4][1])) / 2 + zGround

            self.startFrame()
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(legMid[3][0] + (-stepRangeHor / 2), legMid[3][1] + (stepRangeVert / 2), zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(legMid[6][0] + (stepRangeHor / 2), legMid[6][1] + (stepRangeVert / 2), zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(legMid[2][0] - (-stepRangeHor / 2), legMid[2][1] - (stepRangeVert / 2), zGround2, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(legMid[5][0] - (stepRangeHor / 2), legMid[5][1] - (stepRangeVert / 2), zGround5, 5, speedMod * 200)
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(legMid[1][0], legMid[1][1], zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(legMid[4][0], legMid[4][1], zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 1:
            if(keepLeveled):
                zAir3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legMid[3][1])) / 2 + zAir
                zAir6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legMid[6][1])) / 2 + zAir
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legMid[2][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legMid[5][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legMid[1][1] + (stepRangeVert / 4)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legMid[4][1] + (stepRangeVert / 4)) / 2 + zGround

            self.startFrame()
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(legMid[3][0], legMid[3][1], zAir3, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(legMid[6][0], legMid[6][1], zAir6, 6, speedMod * 200)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(legMid[2][0] - (-stepRangeHor / 4), legMid[2][1] - (stepRangeVert / 4), zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(legMid[5][0] - (stepRangeHor / 4), legMid[5][1] - (stepRangeVert / 4), zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(legMid[1][0] + (stepRangeHor / 4), legMid[1][1] + (stepRangeVert / 4), zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(legMid[4][0] + (-stepRangeHor / 4), legMid[4][1] + (stepRangeVert / 4), zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 2:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legMid[3][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legMid[6][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legMid[2][1])) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legMid[5][1])) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legMid[1][1] + (stepRangeVert / 2)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legMid[4][1] + (stepRangeVert / 2)) / 2 + zGround

            self.startFrame()
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(legMid[3][0] - (-stepRangeHor / 2), legMid[3][1] - (stepRangeVert / 2), zGround3, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(legMid[6][0] - (stepRangeHor / 2), legMid[6][1] - (stepRangeVert / 2), zGround6, 6, speedMod * 200)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(legMid[2][0], legMid[2][1], zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(legMid[5][0], legMid[5][1], zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(legMid[1][0] + (stepRangeHor / 2), legMid[1][1] + (stepRangeVert / 2), zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(legMid[4][0] + (-stepRangeHor / 2), legMid[4][1] + (stepRangeVert / 2), zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 3:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legMid[3][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legMid[6][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legMid[2][1]) + (stepRangeVert / 4)) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legMid[5][1]) + (stepRangeVert / 4)) / 2 + zGround
                zAir1 = math.sin(self.realYAngle) * (self.bodytoSensor - legMid[1][1]) / 2 + zAir
                zAir4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legMid[4][1]) / 2 + zAir

            self.startFrame()
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(legMid[3][0] - (-stepRangeHor / 4), legMid[3][1] - (stepRangeVert / 4), zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(legMid[6][0] - (stepRangeHor / 4), legMid[6][1] - (stepRangeVert / 4), zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(legMid[2][0] + (-stepRangeHor / 4), legMid[2][1] + (stepRangeVert / 4), zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(legMid[5][0] + (stepRangeHor / 4), legMid[5][1] + (stepRangeVert / 4), zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(legMid[1][0], legMid[1][1], zAir1, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(legMid[4][0], legMid[4][1], zAir4, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 4:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legMid[3][1])) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legMid[6][1])) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legMid[2][1]) + (stepRangeVert / 2)) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legMid[5][1]) + (stepRangeVert / 2)) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legMid[1][1] - (stepRangeVert / 2)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legMid[4][1] - (stepRangeVert / 2)) / 2 + zGround

            self.startFrame()
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(legMid[3][0], legMid[3][1], zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(legMid[6][0], legMid[6][1], zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(legMid[2][0] + (-stepRangeHor / 2), legMid[2][1] + (stepRangeVert / 2), zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(legMid[5][0] + (stepRangeHor / 2), legMid[5][1] + (stepRangeVert / 2), zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(legMid[1][0] - (stepRangeHor / 2), legMid[1][1] - (stepRangeVert / 2), zGround1, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(legMid[4][0] - (-stepRangeHor / 2), legMid[4][1] - (stepRangeVert / 2), zGround4, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 5:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legMid[3][1]) + (stepRangeVert / 4)) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legMid[6][1]) + (stepRangeVert / 4)) / 2 + zGround
                zAir2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legMid[2][1])) / 2 + zAir
                zAir5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legMid[5][1])) / 2 + zAir
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legMid[1][1] - (stepRangeVert / 4)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legMid[4][1] - (stepRangeVert / 4)) / 2 + zGround
            
        
            self.startFrame()
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(legMid[3][0] + (-stepRangeHor / 4), legMid[3][1] + (stepRangeVert / 4), zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(legMid[6][0] + (stepRangeHor / 4), legMid[6][1] + (stepRangeVert / 4), zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(legMid[2][0], legMid[2][1], zAir2, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(legMid[5][0], legMid[5][1], zAir5, 5, speedMod * 200)
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(legMid[1][0] - (stepRangeHor / 4), legMid[1][1] - (stepRangeVert / 4), zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(legMid[4][0] - (-stepRangeHor / 4), legMid[4][1] - (stepRangeVert / 4), zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        
        return totalTime

    def turnRun(self, xDirection, yDirection, frameNr, speedMod=1):
        if xDirection < -1:
            xDirection = -1
            print("xDirection in turnRun can't be lower than -1. It was modified from " + str(xDirection) + " to -1")
        if xDirection > 1:
            xDirection = 1
            print("xDirection in turnRun can't be higher than 1. It was modified from " + str(xDirection) + " to 1")
        if yDirection < -1:
            yDirection = -1
            print("yDirection in turnRun can't be lower than -1. It was modified from " + str(yDirection) + " to -1")
        if yDirection > 1:
            yDirection = 1
            print("yDirection in turnRun can't be higher than 1. It was modified from " + str(yDirection) + " to 1")

        xDirection = round(xDirection, 2)
        yDirection = round(yDirection, 2)

        midXOffset = 0
        if xDirection == 0:
            midXOffset = 10000000
        elif yDirection == 0:
            midXOffset = 0
        else:
            midXOffset = 100 * abs(yDirection) * (1 / xDirection)

        stepSizeCm = 18.53 / 4

        legMid = self.legRunMid

        zGround = 5
        zAir = 3

        turnWalkInfo = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
        highestTotalDistance = 0

        for x in range(1, 7):
            legDistanceFromCenter = 0.0  # 6
            if x == 6:  # left mid
                legDistanceFromCenter = 10.45 + midXOffset
            elif x == 3:  # right mid
                legDistanceFromCenter = 10.45 - midXOffset
            elif x == 1 or x == 5:  # left corners
                legDistanceFromCenter = math.sqrt(
                    (self.cornerCoxaXDistanceFromCenter + midXOffset) ** 2 + self.cornerCoxaYDistanceFromCenter ** 2)
            elif x == 2 or x == 4:  # right corners
                legDistanceFromCenter = math.sqrt(
                    (self.cornerCoxaXDistanceFromCenter - midXOffset) ** 2 + self.cornerCoxaYDistanceFromCenter ** 2)

            legLength = math.sqrt((self.stockLegLength + legMid[x][0]) ** 2 + legMid[x][1] ** 2)
            positionDifference = math.sqrt(legMid[x][0] ** 2 + legMid[x][1] ** 2)
            extraCoxaAngle = math.acos((legLength ** 2 + self.stockLegLength ** 2 - positionDifference ** 2) / (
            2 * legLength * self.stockLegLength)) / math.pi * 180
            coxaAngle = 0
            if x == 1 or x == 5:
                if midXOffset < -self.cornerCoxaYDistanceFromCenter:
                    coxaAngle = 90 - math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4
                else:
                    coxaAngle = 90 + math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4
            elif x == 2 or x == 4:
                if midXOffset < self.cornerCoxaYDistanceFromCenter:
                    coxaAngle = 90 + math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4
                else:
                    coxaAngle = 90 - math.acos(
                        self.cornerCoxaYDistanceFromCenter / legDistanceFromCenter) / math.pi * 180  # 4

            actualCoxaAngle = coxaAngle + extraCoxaAngle

            totalDistance = 0
            if x == 3 or x == 6:
                totalDistance = abs(legDistanceFromCenter + legLength)
            else:
                totalDistance = math.sqrt(
                    legDistanceFromCenter ** 2 + legLength ** 2 - 2 * legDistanceFromCenter * legLength * math.cos(
                        actualCoxaAngle * math.pi / 180))

            if totalDistance > highestTotalDistance:
                highestTotalDistance = totalDistance

            angleFromCenter = 0
            if x == 3:
                if midXOffset < self.sideLegDistanceFromCenter:
                    angleFromCenter = 0
                else:
                    angleFromCenter = 180
            elif x == 6:
                if midXOffset < -self.sideLegDistanceFromCenter:
                    angleFromCenter = 180
                else:
                    angleFromCenter = 0
            else:
                angleFromCenter1 = coxaAngle
                angleFromCenter2 = math.acos((totalDistance ** 2 + legDistanceFromCenter ** 2 - legLength ** 2) / (
                2 * totalDistance * legDistanceFromCenter)) / math.pi * 180
                angleFromCenter = angleFromCenter1 + angleFromCenter2

            angleCompensatorX = totalDistance * math.cos(angleFromCenter * math.pi / 180) - totalDistance
            angleCompensatorY = totalDistance * math.sin(angleFromCenter * math.pi / 180) - totalDistance

            turnWalkInfo[x]["totalDistance"] = totalDistance
            turnWalkInfo[x]["angleFromCenter"] = angleFromCenter
            turnWalkInfo[x]["angleCompensatorX"] = angleCompensatorX
            turnWalkInfo[x]["angleCompensatorY"] = angleCompensatorY

        subCorner = math.acos((highestTotalDistance ** 2 + stepSizeCm ** 2 - highestTotalDistance ** 2) / (2 * highestTotalDistance * stepSizeCm)) / math.pi * 180
        stepSizeDegrees = 180 - (subCorner * 2)
        if (yDirection == -1) ^ (xDirection < 0):
            stepSizeDegrees *= -1

        frameNr = frameNr % 8

        leg135FrameNr = frameNr
        leg246FrameNr = (frameNr + 4) % 8

        print("Frame " + str(frameNr))

        self.startFrame()
        if leg135FrameNr < 5:
            x = legMid[1][0] - (turnWalkInfo[1]["totalDistance"] * math.cos((turnWalkInfo[1]["angleFromCenter"] - (2 - leg135FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[1]["totalDistance"] - turnWalkInfo[1]["angleCompensatorX"])
            y = legMid[1][1] - (turnWalkInfo[1]["totalDistance"] * math.sin((turnWalkInfo[1]["angleFromCenter"] - (2 - leg135FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[1]["totalDistance"] - turnWalkInfo[1]["angleCompensatorY"])
            print("leg 1 x:"+str(x)+"y:"+str(y))
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(x, y, (zGround + 0.3) if leg135FrameNr == 1 else zGround, 1, speedMod * 100)
            x = legMid[3][0] + (turnWalkInfo[3]["totalDistance"] * math.cos((turnWalkInfo[3]["angleFromCenter"] - (2 - leg135FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[3]["totalDistance"] - turnWalkInfo[3]["angleCompensatorX"])
            y = legMid[3][1] - (turnWalkInfo[3]["totalDistance"] * math.sin((turnWalkInfo[3]["angleFromCenter"] - (2 - leg135FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[3]["totalDistance"] - turnWalkInfo[3]["angleCompensatorY"])
            print("leg 3 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(x, y, (zGround + 0.3) if leg135FrameNr == 1 else zGround, 3, speedMod * 100)
            x = legMid[5][0] + (turnWalkInfo[5]["totalDistance"] * math.cos((turnWalkInfo[5]["angleFromCenter"] - (2 - leg135FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[5]["totalDistance"] - turnWalkInfo[5]["angleCompensatorX"])
            y = legMid[5][1] - (turnWalkInfo[5]["totalDistance"] * math.sin((turnWalkInfo[5]["angleFromCenter"] - (2 - leg135FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[5]["totalDistance"] - turnWalkInfo[5]["angleCompensatorY"])
            print("leg 5 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(x, y, (zGround + 0.3) if leg135FrameNr == 1 else zGround, 5, speedMod * 100)
        else:
            x = legMid[1][0] - (turnWalkInfo[1]["totalDistance"] * math.cos((turnWalkInfo[1]["angleFromCenter"] - (-2 + (leg135FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[1]["totalDistance"] - turnWalkInfo[1]["angleCompensatorX"])
            y = legMid[1][1] - (turnWalkInfo[1]["totalDistance"] * math.sin((turnWalkInfo[1]["angleFromCenter"] - (-2 + (leg135FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[1]["totalDistance"] - turnWalkInfo[1]["angleCompensatorY"])
            print("leg 1 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(x, y, zAir, 1, speedMod * 100)
            x = legMid[3][0] + (turnWalkInfo[3]["totalDistance"] * math.cos((turnWalkInfo[3]["angleFromCenter"] - (-2 + (leg135FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[3]["totalDistance"] - turnWalkInfo[3]["angleCompensatorX"])
            y = legMid[3][1] - (turnWalkInfo[3]["totalDistance"] * math.sin((turnWalkInfo[3]["angleFromCenter"] - (-2 + (leg135FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[3]["totalDistance"] - turnWalkInfo[3]["angleCompensatorY"])
            print("leg 3 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(x, y, zAir, 3, speedMod * 100)
            x = legMid[5][0] + (turnWalkInfo[5]["totalDistance"] * math.cos((turnWalkInfo[5]["angleFromCenter"] - (-2 + (leg135FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[5]["totalDistance"] - turnWalkInfo[5]["angleCompensatorX"])
            y = legMid[5][1] - (turnWalkInfo[5]["totalDistance"] * math.sin((turnWalkInfo[5]["angleFromCenter"] - (-2 + (leg135FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[5]["totalDistance"] - turnWalkInfo[5]["angleCompensatorY"])
            print("leg 5 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(x, y, zAir, 5, speedMod * 100)

        if leg246FrameNr < 5:
            x = legMid[2][0] + (turnWalkInfo[2]["totalDistance"] * math.cos((turnWalkInfo[2]["angleFromCenter"] - (2 - leg246FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[2]["totalDistance"] - turnWalkInfo[2]["angleCompensatorX"])
            y = legMid[2][1] + (turnWalkInfo[2]["totalDistance"] * math.sin((turnWalkInfo[2]["angleFromCenter"] - (2 - leg246FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[2]["totalDistance"] - turnWalkInfo[2]["angleCompensatorY"])
            print("leg 2 x:"+str(x)+"y:"+str(y))
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(x, y, (zGround + 0.3) if leg135FrameNr == 1 else zGround, 2, speedMod * 100)
            x = legMid[4][0] - (turnWalkInfo[4]["totalDistance"] * math.cos((turnWalkInfo[4]["angleFromCenter"] - (2 - leg246FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[4]["totalDistance"] - turnWalkInfo[4]["angleCompensatorX"])
            y = legMid[4][1] + (turnWalkInfo[4]["totalDistance"] * math.sin((turnWalkInfo[4]["angleFromCenter"] - (2 - leg246FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[4]["totalDistance"] - turnWalkInfo[4]["angleCompensatorY"])
            print("leg 4 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(x, y, (zGround + 0.3) if leg135FrameNr == 1 else zGround, 4, speedMod * 100)
            x = legMid[6][0] + (turnWalkInfo[6]["totalDistance"] * math.cos((turnWalkInfo[6]["angleFromCenter"] - (2 - leg246FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[6]["totalDistance"] - turnWalkInfo[6]["angleCompensatorX"])
            y = legMid[6][1] + (turnWalkInfo[6]["totalDistance"] * math.sin((turnWalkInfo[6]["angleFromCenter"] - (2 - leg246FrameNr) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[6]["totalDistance"] - turnWalkInfo[6]["angleCompensatorY"])
            print("leg 6 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(x, y, (zGround + 0.3) if leg135FrameNr == 1 else zGround, 6, speedMod * 100)
        else:
            x = legMid[2][0] + (turnWalkInfo[2]["totalDistance"] * math.cos((turnWalkInfo[2]["angleFromCenter"] - (-2 + (leg246FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[2]["totalDistance"] - turnWalkInfo[2]["angleCompensatorX"])
            y = legMid[2][1] + (turnWalkInfo[2]["totalDistance"] * math.sin((turnWalkInfo[2]["angleFromCenter"] - (-2 + (leg246FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[2]["totalDistance"] - turnWalkInfo[2]["angleCompensatorY"])
            print("leg 2 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(x, y, zAir, 2, speedMod * 100)
            x = legMid[4][0] - (turnWalkInfo[4]["totalDistance"] * math.cos((turnWalkInfo[4]["angleFromCenter"] - (-2 + (leg246FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[4]["totalDistance"] - turnWalkInfo[4]["angleCompensatorX"])
            y = legMid[4][1] + (turnWalkInfo[4]["totalDistance"] * math.sin((turnWalkInfo[4]["angleFromCenter"] - (-2 + (leg246FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[4]["totalDistance"] - turnWalkInfo[4]["angleCompensatorY"])
            print("leg 4 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(x, y, zAir, 4, speedMod * 100)
            x = legMid[6][0] + (turnWalkInfo[6]["totalDistance"] * math.cos((turnWalkInfo[6]["angleFromCenter"] - (-2 + (leg246FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[6]["totalDistance"] - turnWalkInfo[6]["angleCompensatorX"])
            y = legMid[6][1] + (turnWalkInfo[6]["totalDistance"] * math.sin((turnWalkInfo[6]["angleFromCenter"] - (-2 + (leg246FrameNr % 4)) * stepSizeDegrees) * math.pi / 180) - turnWalkInfo[6]["totalDistance"] - turnWalkInfo[6]["angleCompensatorY"])
            print("leg 6 x:" + str(x) + "y:" + str(y))
            self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(x, y, zAir, 6, speedMod * 100)
        return self.endFrame()

    def push(self, frameNr, speedMod = 1, direction=1):
        totalTime = 0
        speed = speedMod * 100
        frontLegAngleModifier = 0
        backLegAngleModifier = 0
        zUp = -3
        zDown = 1
        remoteContext = self.spider.remoteController.context
        angleController = remoteContext.aY
        if abs(angleController) > 0.2:
            if angleController > 0:
                #frontLegAngleModifier = angleController * -4
                frontLegAngleModifier = 1
                print("frontLegAngleModifier:", frontLegAngleModifier)
            else:
                #backLegAngleModifier = abs(angleController) * -4
                backLegAngleModifier = 1
                print("backLegAngleModifier:", backLegAngleModifier)


        #leg cordinates
        pushFrames = {
            1: { #out
                1: [-4,-10,zUp],
                2: [-4,-10,zUp],
                3: [0,0,zUp],
                4: [-4,0,zUp],
                5: [-4,0,zUp],
                6: [0,0,zUp]
            },
            2: { #out
                1: [-7,-20,zUp],
                2: [-7,-20,zUp],
                3: [0,0,zUp],
                4: [-7,0,zUp],
                5: [-7,0,zUp],
                6: [0,0,zUp]
            },
            3: { #in
                1: [-7,-16,zDown],
                2: [-7,-16,zDown],
                3: [0,0,zUp],
                4: [-7,4,zDown],
                5: [-7,4,zDown],
                6: [0,0,zUp]
            },
            4: { #in
                1: [-7,-12,zDown],
                2: [-7,-12,zDown],
                3: [0,0,zUp],
                4: [-7,8,zDown],
                5: [-7,8,zDown],
                6: [0,0,zUp]
            },
            5: { #in
                1: [-7,-8,zDown],
                2: [-7,-8,zDown],
                3: [0,0,zUp],
                4: [-7,12,zDown],
                5: [-7,12,zDown],
                6: [0,0,zUp]
            },
            6: { #in
                1: [-7,-4,zDown],
                2: [-7,-4,zDown],
                3: [0,0,zUp],
                4: [-7,16,zDown],
                5: [-7,16,zDown],
                6: [0,0,zUp]
            },
            0: { #in
                1: [-7,0,zDown],
                2: [-7,0,zDown],
                3: [0,0,zUp],
                4: [-7,20,zDown],
                5: [-7,20,zDown],
                6: [0,0,zUp]
            }
        }

        #leg cordinates 2
        pushFrames2 = {
            1: {
                1: [-16, -20, 1],
                2: [-16, -20, 1],
                3: [0, 0, 0],
                4: [-16, 20, 1],
                5: [-16, 20, 1],
                6: [0, 0, 0]
            },
            2: {
                1: [-16, -12, 1],
                2: [-16, -12, 1],
                3: [0, 0, 0],
                4: [-16, 12, 1],
                5: [-16, 12, 1],
                6: [0, 0, 0]
            },
            3: {
                1: [-16, -12, -3],
                2: [-16, -12, -3],
                3: [0, 0, 0],
                4: [-16, 12, 1],
                5: [-16, 12, 1],
                6: [0, 0, 0]
            },
            0: {
                1: [-16, -20, 1],
                2: [-16, -20, 1],
                3: [0, 0, 0],
                4: [-16, 20, 1],
                5: [-16, 20, 1],
                6: [0, 0, 0]
            }
        }
        if direction == 1:
            frameNr = frameNr % len(pushFrames)
        else:
            frameNr = 7 - frameNr % len(pushFrames)

        print("frameNr: ", frameNr)
        self.startFrame()
        if frontLegAngleModifier == 1:
            print("Frontleg")
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(x=-7, y=-20, z=-4, legID=1, speed=speed)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(x=-7, y=-20, z=-4, legID=2, speed=speed)
        else:
            self.sequenceFrame.movements[1] = self.seqCtrl.coordsToLegMovement(x=pushFrames[frameNr][1][0],y=pushFrames[frameNr][1][1],z=pushFrames[frameNr][1][2] + frontLegAngleModifier,legID=1, speed=speed)
            self.sequenceFrame.movements[2] = self.seqCtrl.coordsToLegMovement(x=pushFrames[frameNr][2][0],y=pushFrames[frameNr][2][1],z=pushFrames[frameNr][2][2] + frontLegAngleModifier,legID=2, speed=speed)
        self.sequenceFrame.movements[3] = self.seqCtrl.coordsToLegMovement(x=pushFrames[frameNr][3][0], y=pushFrames[frameNr][3][1], z=pushFrames[frameNr][3][2], legID=3, speed=speed)
        self.sequenceFrame.movements[6] = self.seqCtrl.coordsToLegMovement(x=pushFrames[frameNr][6][0],y=pushFrames[frameNr][6][1],z=pushFrames[frameNr][6][2], legID=6,speed=speed)
        if backLegAngleModifier == 1:
            print("Backleg")
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(x=-7, y=20, z=-4, legID=5, speed=speed)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(x=-7, y=20, z=-4, legID=4, speed=speed)
        else:
            self.sequenceFrame.movements[5] = self.seqCtrl.coordsToLegMovement(x=pushFrames[frameNr][5][0],y=pushFrames[frameNr][5][1],z=pushFrames[frameNr][5][2] + backLegAngleModifier, legID=5,speed=speed)
            self.sequenceFrame.movements[4] = self.seqCtrl.coordsToLegMovement(x=pushFrames[frameNr][4][0],y=pushFrames[frameNr][4][1],z=pushFrames[frameNr][4][2] + backLegAngleModifier, legID=4,speed=speed)
        totalTime += self.endFrame()

        return totalTime