import math
from spInDP.LegMovement import LegMovement
from spInDP.SequenceFrame import SequenceFrame

class AnimationController:
    
    legVertMid = {
        1: [-7, -8],
        2: [-7, -8],
        3: [-5, 0],
        4: [-7, 8],
        5: [-7, 8],
        6: [-5, 0]
    }

    legHorMid = {
        1: [-4, -8],
        2: [-4, -8],
        3: [-4, 0],
        4: [-4, 8],
        5: [-4, 8],
        6: [-4, 0]
    }
    legTurnMid = {
        1: [-4, -8],
        2: [-4, -8],
        3: [-4, 0],
        4: [-4, 8],
        5: [-4, 8],
        6: [-4, 0]
    }

    seqCtrl = None
    yAdjustment = 0
    
    bodytoSensorMid = 0  # from mid body to mid coxas X-axis
    bodytoSensor = 12.05 # from mid body to back and front coxas X-axis

    def __init__(self, spider):
        self.spider = spider
        self.seqCtrl = spider.sequenceController


    """
        destination is a sequenceframe
    """
    def safeTransitionTo(self, destination, speed):
        cLegCoords = {}

        for x in range(1,7):
            cLegCoords[x].IKCoordinates = self.spider.sequenceController.getLegCoords(x)

        zSortedLegCoords = sorted(cLegCoords, key=lambda legID: cLegCoords[legID].IKCoordinates[2])
        cGroundedLegs = zSortedLegCoords[-3:] #Get 3 legs with highest z coordinate
        cElevatedLegs    = zSortedLegCoords[:-3] #the other 3 legs

        zSortedDestCoords = sorted(destination.movements, key=lambda legID: destination.movements[legID].IKCoordinates[2])
        destGroundedLegs = zSortedDestCoords[-3:]
        destElevatedLegs = zSortedDestCoords[:-3]
        highestDestZ = destGroundedLegs[2].IKCoordinates[2]
        elevatedZ = highestDestZ - 2

        # if legs are elevated set them to 0,0,highestDestZ
        self.startFrame()
        for legID in cElevatedLegs:
                if cElevatedLegs[legID].IKCoordinates[2] > highestDestZ:
                    self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(0, 0, highestDestZ, legID, speed)
        self.endFrame()

        #after that, one by one, elevate the legs a little and send them to their destination
        for legID in range(1,7):
            destCoords = destGroundedLegs[legID].IKCoordinates
            self.startFrame()
            self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(destCoords[0], destCoords[1], elevatedZ, legID, speed)
            self.endFrame()
            self.startFrame()
            self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(destCoords[0], destCoords[1], destCoords[2], legID, speed)
            self.endFrame()
   

    #Adjust midpoint of the crabwalk to fit through 'het poortje'
    def setWideCrabWalk(self, value):
        if value:
            self.legHorMid[1][1] = -8
            self.legHorMid[2][1] = -8
            self.legHorMid[4][1] = 8
            self.legHorMid[5][1] = 8
        else:
            self.legHorMid[1][1] = -3
            self.legHorMid[2][1] = -3
            self.legHorMid[4][1] = 3
            self.legHorMid[5][1] = 3
    
    def startFrame(self):
        self.sequenceFrame = SequenceFrame()

    def endFrame(self):
        #Add the new frame to the leg queues
        self.seqCtrl.addFrameToQueue(self.sequenceFrame)
        
        ret = self.sequenceFrame.maxMaxExecTime
        self.sequenceFrame.movements = {} #Clear the frame
        self.sequenceFrame = None
        return ret


    def turn(self, direction, frameNr, speedMod = 1):
        totalTime = 0
        
        zGround = 5
        zAir = 2
        
        stepSize = 5
        
        sideLegDistanceFromCenter = 10.45
        cornerLegDistanceFromCenter = 13.845
        stockLegLength = 16.347
        stockCoxaAngle = 119.5

        actualLegLength = math.sqrt((stockLegLength+self.legTurnMid[1][0])**2+self.legTurnMid[1][1]**2)
        actualCoxaAngle = stockCoxaAngle - math.asin(self.legTurnMid[1][1]/actualLegLength)/math.pi*180
        totalDistance = math.sqrt(cornerLegDistanceFromCenter**2 + actualLegLength**2 - 2*cornerLegDistanceFromCenter*actualLegLength*math.cos(actualCoxaAngle*math.pi/180))
        
        beta1 = math.asin((actualLegLength * math.sin(actualCoxaAngle*math.pi/180))/totalDistance)/math.pi*180
        beta2 = stockCoxaAngle-90
        betaSum = beta1+beta2
        
        xMidCompensator = totalDistance*math.cos(betaSum*math.pi/180) - totalDistance
        yMidCompensator = totalDistance*math.sin(betaSum*math.pi/180) - totalDistance
        
        frameNr = frameNr % 6
        seqCtrl = self.spider.sequenceController
        self.startFrame()
        if frameNr == 0:
            x = self.legTurnMid[3][0] + totalDistance * math.cos(-2 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[3][1] + totalDistance * math.sin(-2 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(x, y, zGround, 3, speedMod * 100)
            x = self.legTurnMid[6][0] + totalDistance * math.cos(2 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[6][1] + totalDistance * math.sin(2 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(x, y, zGround, 6, speedMod * 100)
        
            x = self.legTurnMid[2][0] + (totalDistance * math.cos((-2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[2][1] - (totalDistance * math.sin((-2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(x, y, zGround, 2, speedMod * 200)
            x = self.legTurnMid[5][0] + (totalDistance * math.cos((-2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[5][1] + (totalDistance * math.sin((-2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(x, y, zGround, 5, speedMod * 200)
        
            x = self.legTurnMid[1][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[1][1] - (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(x, y, zGround, 1, speedMod * 100)
            x = self.legTurnMid[4][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[4][1] + (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(x, y, zGround, 4, speedMod * 100)
        elif frameNr == 1:
            x = self.legTurnMid[3][0] + totalDistance * math.cos(0 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[3][1] + totalDistance * math.sin(0 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(x, y, zAir, 3, speedMod * 200)
            x = self.legTurnMid[6][0] + totalDistance * math.cos(0 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[6][1] + totalDistance * math.sin(0 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(x, y, zAir, 6, speedMod * 200)

            x = self.legTurnMid[2][0] + (totalDistance * math.cos((-1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[2][1] - (totalDistance * math.sin((-1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(x, y, zGround, 2, speedMod * 100)
            x = self.legTurnMid[5][0] + (totalDistance * math.cos((-1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[5][1] + (totalDistance * math.sin((-1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(x, y, zGround, 5, speedMod * 100)

            x = self.legTurnMid[1][0] + (totalDistance * math.cos((-1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -2.406
            y = self.legTurnMid[1][1] - (totalDistance * math.sin((-1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -9.82
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(x, y, zGround, 1, speedMod * 100)
            x = self.legTurnMid[4][0] + (totalDistance * math.cos((-1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[4][1] + (totalDistance * math.sin((-1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(x, y, zGround, 4, speedMod * 100)
        elif frameNr == 2:
            x = self.legTurnMid[3][0] + totalDistance * math.cos(2 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[3][1] + totalDistance * math.sin(2 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(x, y, zGround, 3, speedMod * 200)
            x = self.legTurnMid[6][0] + totalDistance * math.cos(-2 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[6][1] + totalDistance * math.sin(-2 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(x, y, zGround, 6, speedMod * 200)

            x = self.legTurnMid[2][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[2][1] - (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(x, y, zGround, 2, speedMod * 100)
            x = self.legTurnMid[5][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[5][1] + (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(x, y, zGround, 5, speedMod * 100)

            x = self.legTurnMid[1][0] + (totalDistance * math.cos((-2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -0.977
            y = self.legTurnMid[1][1] - (totalDistance * math.sin((-2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -11.773
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(x, y, zGround, 1, speedMod * 100)
            x = self.legTurnMid[4][0] + (totalDistance * math.cos((-2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[4][1] + (totalDistance * math.sin((-2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(x, y, zGround, 4, speedMod * 100)
        elif frameNr == 3:
            x = self.legTurnMid[3][0] + totalDistance * math.cos(1 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[3][1] + totalDistance * math.sin(1 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(x, y, zGround, 3, speedMod * 100)
            x = self.legTurnMid[6][0] + totalDistance * math.cos(-1 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[6][1] + totalDistance * math.sin(-1 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(x, y, zGround, 6, speedMod * 100)

            x = self.legTurnMid[2][0] + (totalDistance * math.cos((1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[2][1] - (totalDistance * math.sin((1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(x, y, zGround, 2, speedMod * 100)
            x = self.legTurnMid[5][0] + (totalDistance * math.cos((1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[5][1] + (totalDistance * math.sin((1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(x, y, zGround, 5, speedMod * 100)

            x = self.legTurnMid[1][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[1][1] - (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(x, y, zAir, 1, speedMod * 200)
            x = self.legTurnMid[4][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[4][1] + (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(x, y, zAir, 4, speedMod * 200)
        elif frameNr == 4:
            x = self.legTurnMid[3][0] + totalDistance * math.cos(0 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[3][1] + totalDistance * math.sin(0 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(x, y, zGround, 3, speedMod * 100)
            x = self.legTurnMid[6][0] + totalDistance * math.cos(0 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[6][1] + totalDistance * math.sin(0 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(x, y, zGround, 6, speedMod * 100)

            x = self.legTurnMid[2][0] + (totalDistance * math.cos((2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[2][1] - (totalDistance * math.sin((2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(x, y, zGround, 2, speedMod * 100)
            x = self.legTurnMid[5][0] + (totalDistance * math.cos((2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[5][1] + (totalDistance * math.sin((2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(x, y, zGround, 5, speedMod * 100)

            x = self.legTurnMid[1][0] + (totalDistance * math.cos((2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -7.63
            y = self.legTurnMid[1][1] - (totalDistance * math.sin((2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -4.809
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(x, y, zGround, 1, speedMod * 200)
            x = self.legTurnMid[4][0] + (totalDistance * math.cos((2 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[4][1] + (totalDistance * math.sin((2 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(x, y, zGround, 4, speedMod * 200)
        elif frameNr == 5:
            x = self.legTurnMid[3][0] + totalDistance * math.cos(-1 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[3][1] + totalDistance * math.sin(-1 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(x, y, zGround, 3, speedMod * 100)
            x = self.legTurnMid[6][0] + totalDistance * math.cos(1 * stepSize * math.pi / 180) - totalDistance
            y = self.legTurnMid[6][1] + totalDistance * math.sin(1 * stepSize * math.pi / 180)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(x, y, zGround, 6, speedMod * 100)

            x = self.legTurnMid[2][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[2][1] - (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -8
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(x, y, zAir, 2, speedMod * 200)
            x = self.legTurnMid[5][0] + (totalDistance * math.cos((0 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[5][1] + (totalDistance * math.sin((0 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(x, y, zAir, 5, speedMod * 200)

            x = self.legTurnMid[1][0] + (totalDistance * math.cos((1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -5.75
            y = self.legTurnMid[1][1] - (totalDistance * math.sin((1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) + totalDistance  # -9.6746
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(x, y, zGround, 1, speedMod * 100)
            x = self.legTurnMid[4][0] + (totalDistance * math.cos((1 * stepSize + betaSum) * math.pi / 180) - xMidCompensator) - totalDistance  # -4
            y = self.legTurnMid[4][1] + (totalDistance * math.sin((1 * stepSize + betaSum) * math.pi / 180) - yMidCompensator) - totalDistance  # -8
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(x, y, zGround, 4, speedMod * 100)
        totalTime += self.endFrame()
        
        return totalTime
        
    def turnold(self, direction, frameNr, speedMod = 1):
        totalTime = 0
        
        zGround = 5
        zAir = 2
        
        directionStepSize = int(direction) / 4
        
        sideLegDistanceFromCenter = 10.45
        cornerLegDistanceFromCenter = 13.845
        sideLegLengthX = math.sqrt((16.347 + self.legTurnMid[3][0])**2 + abs(self.legTurnMid[3][1])**2)
        cornerLegLength = math.sqrt((16.347 + self.legTurnMid[1][0])**2 + abs(self.legTurnMid[1][1])**2)
        
        sideLegDistance = sideLegDistanceFromCenter + sideLegLengthX
        cornerLegDistanceFront = math.sqrt(cornerLegDistanceFromCenter**2 + cornerLegLength**2 - 2*cornerLegDistanceFromCenter*cornerLegLength*abs(math.cos((119.5+math.asin(-self.legTurnMid[1][1]/cornerLegLength))*math.pi/180)))
        cornerLegDistanceBack = math.sqrt(cornerLegDistanceFromCenter**2 + cornerLegLength**2 - 2*cornerLegDistanceFromCenter*cornerLegLength*abs(math.cos((119.5+math.asin(self.legTurnMid[1][1]/cornerLegLength))*math.pi/180)))
        
        frameNr = frameNr % 6
        seqCtrl = self.spider.sequenceController
        if frameNr == 0:
            self.startFrame()
            cosDirection = math.cos(-2*directionStepSize*math.pi/180)
            sinDirection = math.sin(-2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(self.legTurnMid[3][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[3][1] + sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(self.legTurnMid[6][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[6][1] + (-sinDirection) * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(2*directionStepSize*math.pi/180)
            sinDirection = math.sin(2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(self.legTurnMid[2][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[2][1] + sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(self.legTurnMid[5][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[5][1] + (-sinDirection) * cornerLegDistanceBack, zGround, 5, speedMod * 200)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(self.legTurnMid[1][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[1][1] + (-sinDirection) * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(self.legTurnMid[4][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[4][1] + sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 1:
            self.startFrame()
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(self.legTurnMid[3][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[3][1] + sinDirection * sideLegDistance, zAir, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(self.legTurnMid[6][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[6][1] + (-sinDirection) * sideLegDistance, zAir, 6, speedMod * 200)
            
            cosDirection = math.cos(1*directionStepSize*math.pi/180)
            sinDirection = math.sin(1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(self.legTurnMid[2][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[2][1] + sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(self.legTurnMid[5][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[5][1] + (-sinDirection) * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(-1*directionStepSize*math.pi/180)
            sinDirection = math.sin(-1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(self.legTurnMid[1][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[1][1] + (-sinDirection) * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(self.legTurnMid[4][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[4][1] + sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 2:
            self.startFrame()
            cosDirection = math.cos(2*directionStepSize*math.pi/180)
            sinDirection = math.sin(2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(self.legTurnMid[3][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[3][1] + sinDirection * sideLegDistance, zGround, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(self.legTurnMid[6][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[6][1] + (-sinDirection) * sideLegDistance, zGround, 6, speedMod * 200)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(self.legTurnMid[2][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[2][1] + sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(self.legTurnMid[5][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[5][1] + (-sinDirection) * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(-2*directionStepSize*math.pi/180)
            sinDirection = math.sin(-2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(self.legTurnMid[1][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[1][1] + (-sinDirection) * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(self.legTurnMid[4][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[4][1] + sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 3:
            self.startFrame()
            cosDirection = math.cos(1*directionStepSize*math.pi/180)
            sinDirection = math.sin(1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(self.legTurnMid[3][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[3][1] + sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(self.legTurnMid[6][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[6][1] + (-sinDirection) * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(-1*directionStepSize*math.pi/180)
            sinDirection = math.sin(-1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(self.legTurnMid[2][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[2][1] + sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(self.legTurnMid[5][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[5][1] + (-sinDirection) * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(self.legTurnMid[1][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[1][1] + (-sinDirection) * cornerLegDistanceFront, zAir, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(self.legTurnMid[4][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[4][1] + sinDirection * cornerLegDistanceBack, zAir, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 4:
            self.startFrame()
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(self.legTurnMid[3][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[3][1] + sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(self.legTurnMid[6][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[6][1] + (-sinDirection) * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(-2*directionStepSize*math.pi/180)
            sinDirection = math.sin(-2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(self.legTurnMid[2][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[2][1] + sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(self.legTurnMid[5][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[5][1] + (-sinDirection) * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(2*directionStepSize*math.pi/180)
            sinDirection = math.sin(2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(self.legTurnMid[1][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[1][1] + (-sinDirection) * cornerLegDistanceFront, zGround, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(self.legTurnMid[4][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[4][1] + sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 5:
            self.startFrame()
            cosDirection = math.cos(-1*directionStepSize*math.pi/180)
            sinDirection = math.sin(-1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(self.legTurnMid[3][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[3][1] + sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(self.legTurnMid[6][0] + (cosDirection * sideLegDistance - sideLegDistance), self.legTurnMid[6][1] + (-sinDirection) * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(self.legTurnMid[2][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[2][1] + sinDirection * cornerLegDistanceFront, zAir, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(self.legTurnMid[5][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[5][1] + (-sinDirection) * cornerLegDistanceBack, zAir, 5, speedMod * 200)
            
            cosDirection = math.cos(1*directionStepSize*math.pi/180)
            sinDirection = math.sin(1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(self.legTurnMid[1][0] + (cosDirection * cornerLegDistanceFront - cornerLegDistanceFront), self.legTurnMid[1][1] + (-sinDirection) * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(self.legTurnMid[4][0] + (cosDirection * cornerLegDistanceBack - cornerLegDistanceBack), self.legTurnMid[4][1] + sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        
        return totalTime

    realYAngle = 0
    yAdjustment = 0
    def walk(self, direction, frameNr, speedMod = 1, keepLeveled = False):
        totalTime = 0
        
        
        
        
        cosDirection = math.cos(int(direction)*math.pi/180)
        sinDirection = math.sin(int(direction)*math.pi/180)
        stepRangeVert = cosDirection * 14
        stepRangeHor = sinDirection * 8



        zGround = 5 #When not using keepLeveled
        zAir = 2 #When not using keepLeveled
        if(keepLeveled):
            
            
            zGround = 7
            zAir = 5
          
            #Start measuring so we can intergrate the gyro values
            #make sure the spider is leveled when calling this
            self.spider.sensorDataProvider.startMeasuring() 
            cAccelY = float(self.spider.sensorDataProvider.getSmoothAccelerometer()[1])
            if abs(cAccelY * (180 / math.pi)) < 3:
                cAccelY = 0
            
            self.realYAngle = self.yAdjustment + cAccelY
            self.yAdjustment += cAccelY
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

        

        legActualMid = {
            1: [self.legHorMid[1][0] + abs(cosDirection) * (self.legVertMid[1][0]-self.legHorMid[1][0]), self.legHorMid[1][1] + abs(cosDirection) * (self.legVertMid[1][1]-self.legHorMid[1][1])],
            2: [self.legHorMid[2][0] + abs(cosDirection) * (self.legVertMid[2][0]-self.legHorMid[2][0]), self.legHorMid[2][1] + abs(cosDirection) * (self.legVertMid[2][1]-self.legHorMid[2][1])],
            3: [self.legHorMid[3][0] + abs(cosDirection) * (self.legVertMid[3][0]-self.legHorMid[3][0]), self.legHorMid[3][1] + abs(cosDirection) * (self.legVertMid[3][1]-self.legHorMid[3][1])],
            4: [self.legHorMid[4][0] + abs(cosDirection) * (self.legVertMid[4][0]-self.legHorMid[4][0]), self.legHorMid[4][1] + abs(cosDirection) * (self.legVertMid[4][1]-self.legHorMid[4][1])],
            5: [self.legHorMid[5][0] + abs(cosDirection) * (self.legVertMid[5][0]-self.legHorMid[5][0]), self.legHorMid[5][1] + abs(cosDirection) * (self.legVertMid[5][1]-self.legHorMid[5][1])],
            6: [self.legHorMid[6][0] + abs(cosDirection) * (self.legVertMid[6][0]-self.legHorMid[6][0]), self.legHorMid[6][1] + abs(cosDirection) * (self.legVertMid[6][1]-self.legHorMid[6][1])]
        }
        
        frameNr = frameNr % 6
        seqCtrl = self.seqCtrl
        if frameNr == 0:
            if(keepLeveled):
                zGround3 = -math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legActualMid[3][1] + (stepRangeVert / 2))) / 2 + zGround
                zGround6 = -math.sin(self.realYAngle) * (self.bodytoSensorMid + (legActualMid[6][1] + (stepRangeVert / 2))) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legActualMid[2][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legActualMid[5][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - (legActualMid[1][1])) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legActualMid[4][1])) / 2 + zGround
                
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] + (-stepRangeHor / 2), legActualMid[3][1] + (stepRangeVert / 2), zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] + (stepRangeHor / 2), legActualMid[6][1] + (stepRangeVert / 2), zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] - (-stepRangeHor / 2), legActualMid[2][1] - (stepRangeVert / 2), zGround2, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] - (stepRangeHor / 2), legActualMid[5][1] - (stepRangeVert / 2), zGround5, 5, speedMod * 200)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0], legActualMid[1][1], zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0], legActualMid[4][1], zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 1:
            if(keepLeveled):
                zAir3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legActualMid[3][1])) / 2 + zAir
                zAir6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legActualMid[6][1])) / 2 + zAir
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legActualMid[2][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legActualMid[5][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legActualMid[1][1] + (stepRangeVert / 4)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legActualMid[4][1] + (stepRangeVert / 4)) / 2 + zGround
        
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0], legActualMid[3][1], zAir3, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0], legActualMid[6][1], zAir6, 6, speedMod * 200)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] - (-stepRangeHor / 4), legActualMid[2][1] - (stepRangeVert / 4), zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] - (stepRangeHor / 4), legActualMid[5][1] - (stepRangeVert / 4), zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] + (stepRangeHor / 4), legActualMid[1][1] + (stepRangeVert / 4), zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] + (-stepRangeHor / 4), legActualMid[4][1] + (stepRangeVert / 4), zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 2:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legActualMid[3][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legActualMid[6][1] - (stepRangeVert / 2))) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legActualMid[2][1])) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legActualMid[5][1])) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legActualMid[1][1] + (stepRangeVert / 2)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legActualMid[4][1] + (stepRangeVert / 2)) / 2 + zGround
        
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] - (-stepRangeHor / 2), legActualMid[3][1] - (stepRangeVert / 2), zGround3, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] - (stepRangeHor / 2), legActualMid[6][1] - (stepRangeVert / 2), zGround6, 6, speedMod * 200)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0], legActualMid[2][1], zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0], legActualMid[5][1], zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] + (stepRangeHor / 2), legActualMid[1][1] + (stepRangeVert / 2), zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] + (-stepRangeHor / 2), legActualMid[4][1] + (stepRangeVert / 2), zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 3:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legActualMid[3][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legActualMid[6][1] - (stepRangeVert / 4))) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legActualMid[2][1]) + (stepRangeVert / 4)) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legActualMid[5][1]) + (stepRangeVert / 4)) / 2 + zGround
                zAir1 = math.sin(self.realYAngle) * (self.bodytoSensor - legActualMid[1][1]) / 2 + zAir
                zAir4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legActualMid[4][1]) / 2 + zAir
        
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] - (-stepRangeHor / 4), legActualMid[3][1] - (stepRangeVert / 4), zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] - (stepRangeHor / 4), legActualMid[6][1] - (stepRangeVert / 4), zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] + (-stepRangeHor / 4), legActualMid[2][1] + (stepRangeVert / 4), zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] + (stepRangeHor / 4), legActualMid[5][1] + (stepRangeVert / 4), zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0], legActualMid[1][1], zAir1, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0], legActualMid[4][1], zAir4, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 4:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legActualMid[3][1])) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legActualMid[6][1])) / 2 + zGround
                zGround2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legActualMid[2][1]) + (stepRangeVert / 2)) / 2 + zGround
                zGround5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legActualMid[5][1]) + (stepRangeVert / 2)) / 2 + zGround
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legActualMid[1][1] - (stepRangeVert / 2)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legActualMid[4][1] - (stepRangeVert / 2)) / 2 + zGround
        
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0], legActualMid[3][1], zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0], legActualMid[6][1], zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] + (-stepRangeHor / 2), legActualMid[2][1] + (stepRangeVert / 2), zGround2, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] + (stepRangeHor / 2), legActualMid[5][1] + (stepRangeVert / 2), zGround5, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] - (stepRangeHor / 2), legActualMid[1][1] - (stepRangeVert / 2), zGround1, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] - (-stepRangeHor / 2), legActualMid[4][1] - (stepRangeVert / 2), zGround4, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 5:
            if(keepLeveled):
                zGround3 = math.sin(self.realYAngle) * (self.bodytoSensorMid + abs(legActualMid[3][1]) + (stepRangeVert / 4)) / 2 + zGround
                zGround6 = math.sin(self.realYAngle) * (self.bodytoSensorMid + (legActualMid[6][1]) + (stepRangeVert / 4)) / 2 + zGround
                zAir2 = math.sin(self.realYAngle) * (self.bodytoSensor - (legActualMid[2][1])) / 2 + zAir
                zAir5 = -math.sin(self.realYAngle) * (self.bodytoSensor + (legActualMid[5][1])) / 2 + zAir
                zGround1 = math.sin(self.realYAngle) * (self.bodytoSensor - legActualMid[1][1] - (stepRangeVert / 4)) / 2 + zGround
                zGround4 = -math.sin(self.realYAngle) * (self.bodytoSensor + legActualMid[4][1] - (stepRangeVert / 4)) / 2 + zGround
            
        
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] + (-stepRangeHor / 4), legActualMid[3][1] + (stepRangeVert / 4), zGround3, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] + (stepRangeHor / 4), legActualMid[6][1] + (stepRangeVert / 4), zGround6, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0], legActualMid[2][1], zAir2, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0], legActualMid[5][1], zAir5, 5, speedMod * 200)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] - (stepRangeHor / 4), legActualMid[1][1] - (stepRangeVert / 4), zGround1, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] - (-stepRangeHor / 4), legActualMid[4][1] - (stepRangeVert / 4), zGround4, 4, speedMod * 100)
            totalTime += self.endFrame()
        
        return totalTime
