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

    seqCtrl = None;

    def __init__(self, spider):
        self.spider = spider
        self.seqCtrl = spider.sequenceController


    """
        FIND ANOTHER WAY TO SORT A DICTIONAIRY
    """
    # def blendToFrame(self, destination, speed):
    #     cLegCoords = {}

    #     for x in range(1,7):
    #         cLegCoords[x].IKCoordinates = self.spider.sequenceController.getLegCoords(x)

    #     zSortedLegCoords = cLegCoords.sort(key=lambda leg: leg.IKCoordinates[2])
    #     cGroundedLegs = zSortedLegCoords[-3:] #Get 3 legs with highest z coordinate
    #     cElevatedLegs    = zSortedLegCoords[:-3] #the other 3 legs

    #     zSortedDestCoords = destination.movements.sort(key=lambda leg: leg.IKCoordinates[2])
    #     destGroundedLegs = zSortedDestCoords[-3:]
    #     destElevatedLegs = zSortedDestCoords[:-3]
    #     highestDestZ = destGroundedLegs[2].IKCoordinates[2]
    #     elevatedZ = highestDestZ - 2

    #     # if legs are elevated set them to 0,0,highestDestZ
    #     self.startFrame()
    #     for legID in cElevatedLegs:
    #             if cElevatedLegs[legID].IKCoordinates[2] > highestDestZ:
    #                 self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(0, 0, highestDestZ, legID, speed)
    #     self.endFrame()

    #     #after that, one by one, elevate the legs a little and send them to their destination
    #     for legID in range(1,7):
    #         destCoords = destGroundedLegs[legID].IKCoordinates
    #         self.startFrame()
    #         self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(destCoords[0], destCoords[1], elevatedZ, legID, speed)
    #         self.endFrame()
    #         self.startFrame()
    #         self.sequenceFrame.movements[legID] = self.seqCtrl.coordsToLegMovement(destCoords[0], destCoords[1], destCoords[2], legID, speed)
    #         self.endFrame()
    

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
        scaledMovements = self.sequenceFrame.getScaledMovements()
        for x in range(1, 7):
            mov = scaledMovements.get(x, None)
            # Create an 'empty movement
            if (mov is None):
                mov = LegMovement()
                mov.empty = True 
                mov.maxExecTime = self.sequenceFrame.maxMaxExecTime
                
            self.spider.sequenceController.legQueue[x].put(mov)
            
        ret = self.sequenceFrame.maxMaxExecTime
        self.sequenceFrame.movements = {} #Clear the previous frame
        self.sequenceFrame = None
        return ret

    def turn(self, direction, frameNr, speedMod = 1):
        totalTime = 0
        
        zGround = 5
        zAir = 2
        steppingRange = 8
        
        directionStepSize = int(direction) / 4
        
        sideLegDistanceFromCenter = 10.45
        cornerLegDistanceFromCenter = 13.845
        sideLegLengthX = math.sqrt((16.347 + self.legTurnMid[3][0])**2 + abs(self.legTurnMid[3][1])**2)
        cornerLegLength = math.sqrt((16.347 + self.legTurnMid[1][0])**2 + abs(self.legTurnMid[1][1])**2)
        
        sideLegDistance = math.sqrt(sideLegDistanceFromCenter**2 + sideLegLengthX**2 - 2*sideLegDistanceFromCenter*sideLegLengthX*math.cos(0*math.pi/180))
        cornerLegDistanceFront = math.sqrt(cornerLegDistanceFromCenter**2 + cornerLegLength**2 - 2*cornerLegDistanceFromCenter*cornerLegLength*abs(math.cos((119.5+math.asin(-self.legTurnMid[1][1]/cornerLegLength))*math.pi/180)))
        cornerLegDistanceBack = math.sqrt(cornerLegDistanceFromCenter**2 + cornerLegLength**2 - 2*cornerLegDistanceFromCenter*cornerLegLength*abs(math.cos((119.5+math.asin(self.legTurnMid[1][1]/cornerLegLength))*math.pi/180)))
        
        frameNr = frameNr % 6
        seqCtrl = self.spider.sequenceController;
        if frameNr == 0:
            self.startFrame()
            cosDirection = math.cos(-2*directionStepSize*math.pi/180)
            sinDirection = math.sin(-2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, -sinDirection * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(2*directionStepSize*math.pi/180)
            sinDirection = math.sin(2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, -sinDirection * cornerLegDistanceBack, zGround, 5, speedMod * 200)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, -sinDirection * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 1:
            self.startFrame()
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, sinDirection * sideLegDistance, zAir, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, -sinDirection * sideLegDistance, zAir, 6, speedMod * 200)
            
            cosDirection = math.cos(1*directionStepSize*math.pi/180)
            sinDirection = math.sin(1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, -sinDirection * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(-1*directionStepSize*math.pi/180)
            sinDirection = math.sin(-1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, -sinDirection * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 2:
            self.startFrame()
            cosDirection = math.cos(2*directionStepSize*math.pi/180)
            sinDirection = math.sin(2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, sinDirection * sideLegDistance, zGround, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, -sinDirection * sideLegDistance, zGround, 6, speedMod * 200)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, -sinDirection * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(-2*directionStepSize*math.pi/180)
            sinDirection = math.sin(-2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, -sinDirection * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 3:
            self.startFrame()
            cosDirection = math.cos(1*directionStepSize*math.pi/180)
            sinDirection = math.sin(1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, -sinDirection * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(-1*directionStepSize*math.pi/180)
            sinDirection = math.sin(-1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, -sinDirection * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, -sinDirection * cornerLegDistanceFront, zAir, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, sinDirection * cornerLegDistanceBack, zAir, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 4:
            self.startFrame()
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, -sinDirection * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(-2*directionStepSize*math.pi/180)
            sinDirection = math.sin(-2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, sinDirection * cornerLegDistanceFront, zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, -sinDirection * cornerLegDistanceBack, zGround, 5, speedMod * 100)
            
            cosDirection = math.cos(2*directionStepSize*math.pi/180)
            sinDirection = math.sin(2*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, -sinDirection * cornerLegDistanceFront, zGround, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 5:
            self.startFrame()
            cosDirection = math.cos(-1*directionStepSize*math.pi/180)
            sinDirection = math.sin(-1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, sinDirection * sideLegDistance, zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(cosDirection * sideLegDistance - sideLegDistance, -sinDirection * sideLegDistance, zGround, 6, speedMod * 100)
            
            cosDirection = math.cos(0*directionStepSize*math.pi/180)
            sinDirection = math.sin(0*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, sinDirection * cornerLegDistanceFront, zAir, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, -sinDirection * cornerLegDistanceBack, zAir, 5, speedMod * 200)
            
            cosDirection = math.cos(1*directionStepSize*math.pi/180)
            sinDirection = math.sin(1*directionStepSize*math.pi/180)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceFront - cornerLegDistanceFront, -sinDirection * cornerLegDistanceFront, zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(cosDirection * cornerLegDistanceBack - cornerLegDistanceBack, sinDirection * cornerLegDistanceBack, zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        
        return totalTime
        
    def walk(self, direction, frameNr, speedMod = 1):
        totalTime = 0
        
        zGround = 5
        zAir = 2
        cosDirection = math.cos(int(direction)*math.pi/180)
        sinDirection = math.sin(int(direction)*math.pi/180)
        stepRangeVert = cosDirection * 16
        stepRangeHor = sinDirection * 8

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
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] + (-stepRangeHor / 2), legActualMid[3][1] + (stepRangeVert / 2), zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] + (stepRangeHor / 2), legActualMid[6][1] + (stepRangeVert / 2), zGround, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] - (-stepRangeHor / 2), legActualMid[2][1] - (stepRangeVert / 2), zGround, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] - (stepRangeHor / 2), legActualMid[5][1] - (stepRangeVert / 2), zGround, 5, speedMod * 200)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0], legActualMid[1][1], zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0], legActualMid[4][1], zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 1:
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0], legActualMid[3][1], zAir, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0], legActualMid[6][1], zAir, 6, speedMod * 200)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] - (-stepRangeHor / 4), legActualMid[2][1] - (stepRangeVert / 4), zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] - (stepRangeHor / 4), legActualMid[5][1] - (stepRangeVert / 4), zGround, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] + (stepRangeHor / 4), legActualMid[1][1] + (stepRangeVert / 4), zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] + (-stepRangeHor / 4), legActualMid[4][1] + (stepRangeVert / 4), zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 2:
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] - (-stepRangeHor / 2), legActualMid[3][1] - (stepRangeVert / 2), zGround, 3, speedMod * 200)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] - (stepRangeHor / 2), legActualMid[6][1] - (stepRangeVert / 2), zGround, 6, speedMod * 200)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0], legActualMid[2][1], zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0], legActualMid[5][1], zGround, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] + (stepRangeHor / 2), legActualMid[1][1] + (stepRangeVert / 2), zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] + (-stepRangeHor / 2), legActualMid[4][1] + (stepRangeVert / 2), zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        elif frameNr == 3:
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] - (-stepRangeHor / 4), legActualMid[3][1] - (stepRangeVert / 4), zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] - (stepRangeHor / 4), legActualMid[6][1] - (stepRangeVert / 4), zGround, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] + (-stepRangeHor / 4), legActualMid[2][1] + (stepRangeVert / 4), zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] + (stepRangeHor / 4), legActualMid[5][1] + (stepRangeVert / 4), zGround, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0], legActualMid[1][1], zAir, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0], legActualMid[4][1], zAir, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 4:
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0], legActualMid[3][1], zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0], legActualMid[6][1], zGround, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0] + (-stepRangeHor / 2), legActualMid[2][1] + (stepRangeVert / 2), zGround, 2, speedMod * 100)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0] + (stepRangeHor / 2), legActualMid[5][1] + (stepRangeVert / 2), zGround, 5, speedMod * 100)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] - (stepRangeHor / 2), legActualMid[1][1] - (stepRangeVert / 2), zGround, 1, speedMod * 200)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] - (-stepRangeHor / 2), legActualMid[4][1] - (stepRangeVert / 2), zGround, 4, speedMod * 200)
            totalTime += self.endFrame()
        elif frameNr == 5:
            self.startFrame()
            self.sequenceFrame.movements[3] = seqCtrl.coordsToLegMovement(legActualMid[3][0] + (-stepRangeHor / 4), legActualMid[3][1] + (stepRangeVert / 4), zGround, 3, speedMod * 100)
            self.sequenceFrame.movements[6] = seqCtrl.coordsToLegMovement(legActualMid[6][0] + (stepRangeHor / 4), legActualMid[6][1] + (stepRangeVert / 4), zGround, 6, speedMod * 100)
            self.sequenceFrame.movements[2] = seqCtrl.coordsToLegMovement(legActualMid[2][0], legActualMid[2][1], zAir, 2, speedMod * 200)
            self.sequenceFrame.movements[5] = seqCtrl.coordsToLegMovement(legActualMid[5][0], legActualMid[5][1], zAir, 5, speedMod * 200)
            self.sequenceFrame.movements[1] = seqCtrl.coordsToLegMovement(legActualMid[1][0] - (stepRangeHor / 4), legActualMid[1][1] - (stepRangeVert / 4), zGround, 1, speedMod * 100)
            self.sequenceFrame.movements[4] = seqCtrl.coordsToLegMovement(legActualMid[4][0] - (-stepRangeHor / 4), legActualMid[4][1] - (stepRangeVert / 4), zGround, 4, speedMod * 100)
            totalTime += self.endFrame()
        
        return totalTime
