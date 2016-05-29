import time
import math
import threading
import Queue
from spInDP.LegMovement import LegMovement
from spInDP.LegThread import LegThread
from spInDP.SequenceFrame import SequenceFrame


class SequenceController(object):
    """Parses and executes sequences using servos."""

    # Based on physical dimensions of scarJo
    a = 11.0  # Femur length (cm)
    c = 16.8  # Tibia (cm)
    e = 5.60  # height (cm)
    d = 12.24  # Horz. afstand van c tot a (cm)
    lc = 4.107  # Lengte coxa (cm)
    b = math.sqrt(e**2 + d**2)  # diagonal (cm)

    offset = 0
    
    LegOffsets = {
        1: [0,0,0],
        2: [0,0,0],
        3: [0,0,0],
        4: [0,0,0],
        5: [0,0,0],
        6: [0,0,0]
    }
    
    def offsetLeg(self, legID, x,y,z):
        self.LegOffsets[legID] = [x,y,z]

    def __init__(self, spider):
        self.spider = spider
        self.servoController = spider.servoController
        self.legQueue = {}
        self.threadMap = {}
        self.stopped = False

        # Initialize a thread and queue per leg
        for x in range(1, 7):
            self.legQueue[x] = Queue.Queue()
            self.threadMap[x] = LegThread(x, self)
            self.threadMap[x].start()

    def stop(self):
        self.stopped = True

        for key in self.threadMap:
            self.threadMap[key].join()

    def execute(self, sequenceName):
        print("Executing sequence: " + sequenceName)

        if sequenceName == "startup":
            self.executeStartup()

        if sequenceName == "walk":
            self.executeWalk(1)

    
    def executeWalk(self, speedModifier):
        return self.parseSequence("sequences/walk-frame.txt", repeat=1, speedModifier=speedModifier)
        
    def executeStepForward(self):
        return self.parseSequence("sequences/walk-v3.txt", repeat=1, speedModifier=1)
        
    def executeStepBackwards(self):
        return self.parseSequence("sequences/walk-v3-backwards.txt", repeat=1, speedModifier=1)
        
    def executeStepLeft(self):
        return self.parseSequence("sequences/crab-walk.txt", repeat=1, speedModifier=-1)
        
    def executeStepRight(self):
        return self.parseSequence("sequences/crab-walk.txt", repeat=1, speedModifier=1)
        
    def executePreStabLeft(self):
        self.parseSequence("sequences/pre-stab-left.txt", repeat=1, speedModifier=1)
        
    def executeStabLeft(self):
        self.parseSequence("sequences/stab-left.txt", repeat=1, speedModifier=1)
        
    def executePreStabRight(self):
        self.parseSequence("sequences/pre-stab-right.txt", repeat=1, speedModifier=1)
        
    def executeStabRight(self):
        self.parseSequence("sequences/stab-right.txt", repeat=1, speedModifier=1)

    def executeStartup(self):
        return self.parseSequence("sequences/startup.txt")

    sequenceFrame = None

    #Returns the time it takes to execute this sequence in seconds
    def parseSequence(self, filePath, validate=False, speedModifier=1, repeat=1):
        print("Parsing sequence at: " + filePath + " repeating for "  + str(repeat))

        with open(filePath, 'r') as f:
            lines = f.readlines()

        totalTime = 0
        
        words = lines[0].split(' ')
        if (words[0].lower() != "sequence"):
            raise(
                "Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'")
        else:
            if(len(words) > 3):
                self.offset = int(words[3])
            else:
                self.offset = 0

        for x in range(0, repeat):
            print("repeat count: " + str(x))
            lineNr = 0

            if(speedModifier < 0):
                lineNr = len(lines)
                for line in reversed(lines):
                    totalTime += self.interpretLine(line, lineNr, speedModifier, validate)
                    lineNr -= 1
            else:
                lineNr = 1
                for line in lines:
                    totalTime += self.interpretLine(line, lineNr, speedModifier, validate)
                    lineNr += 1

        #if (filePath != "sequences/startup.txt"):
            #self.parseSequence("sequences/startup.txt")
        
        return totalTime
        
    def interpretLine(self, line, lineNr, speedModifier=1, validate=False):
        if(lineNr == 1 or line.lstrip().startswith("#") or len(line.strip()) == 0):
            return 0

        words = line.split(' ')
        command = words[0].lower().rstrip()
        #print("exec command: " + command)

        # Reverse frames when in a backwards direction
        if (speedModifier < 0):
            if (command == "framebegin"):
                command = "frameend"
            elif (command == "frameend"):
                command = "framebegin"

        if(command == "delay"):
            if(len(words) != 2):
                raise NameError("No argument given for delay at line: " + str(lineNr))

            seconds = float(words[1]) / 1000

            if(not validate):
                time.sleep(seconds)

        # Wait for all lengs to complete their queued movements
        elif (command == "waitlegs"):
            for key in self.legQueue:
                self.legQueue[key].join()

        # Wait for a single leg to complete its queued movement
        elif (command == "waitleg"):
            if (len(words) != 2):
                raise NameError(
                    "Wrong amount of arguments for 'waitleg' command. Expected: 1.")

            legId = int(words[1])
            print("waiting for movement of leg " +
                  str(legId) + " to finish")

            # Join will block the calling thread until all items in
            # the queue are processed
            self.legQueue[legId].join()

        elif (command == "print"):
            if (len(words) < 2):
                raise NameError("Nothing to print")

            print(' '.join(words[1:])[:-1])

        elif (command == "include"):
            if (len(words) < 2):
                raise NameError("No sequence file given")

            seq = words[1]
            print("including sequence: " + seq)
            repeat = 1
            if (len(words) > 2):
                repeat = int(words[2])

            self.parseSequence(
                "sequences/" + seq.rstrip() + ".txt", repeat=repeat)

        elif (command == "framebegin"):
            self.sequenceFrame = SequenceFrame()

        elif (command == "frameend"):
            if (self.sequenceFrame is None):
                return 0

            scaledMovements = self.sequenceFrame.getScaledMovements()
            for x in range(1, 7):
                mov = scaledMovements.get(x, None)

                # Create an 'empty movement
                if (mov is None):
                    mov = LegMovement()
                    mov.empty = True
                    mov.maxExecTime = self.sequenceFrame.maxMaxExecTime

                self.legQueue[x].put(mov)

            ret = self.sequenceFrame.maxMaxExecTime
            self.sequenceFrame.movements.clear()
            self.sequenceFrame = None
            
            return ret

        # Control legs
        elif(words[0].lower().startswith('l:')):
            if(len(words) < 2 or len(words) > 3):
                raise NameError("Wrong amount of arguments for servo control: " + str(
                    len(words)) + " at line: " + str(lineNr))

            legID = int(words[0].split(':')[1])
            coords = words[1].split(',')
            if(len(coords) != 3):
                raise NameError(
                    "Wrong amount of coords: " + str(len(coords)) + " (expected 3) at line: " + str(lineNr))

            speed = -1
            if(len(words) == 3):
                speed = int(words[2])

            if(not validate):
                s = 200
                if(speed > 0):
                    s = speed
                    vLeg = self.getServoPos(float(coords[0]), float(
                        coords[1]), float(coords[2]), legID, s * abs(speedModifier))

                    if (vLeg is None):
                        return 0

                    if (self.sequenceFrame is None):
                        self.legQueue[legID].put(vLeg)
                    else:
                        #print ("add leg move to frame")
                        # for i in self.sequenceFrame.movements:
                            # print i, self.sequenceFrame.movements[i].tibia
                        if (self.sequenceFrame.movements.get(legID, None) is not None):
                            raise NameError(
                                "Attempt to move leg " + str(legID) + " more than once in one frame")

                        self.sequenceFrame.movements[legID] = vLeg

        # Control individual servo
        elif(words[0].lower().startswith('s:')):
            if(len(words) < 2 or len(words) > 3):
                raise NameError("Wrong amount of arguments for servo control: " + str(
                    len(words)) + " at line: " + str(lineNr))

            servoID = int(words[0].split(':')[1])
            coords = words[1].split(',')
            if(len(coords) != 1):
                raise NameError(
                    "Wrong amount of coords: " + str(len(coords)) + " (expected 1) at line: " + str(lineNr))

            speed = -1
            if(len(words) == 3):
                speed = int(words[2])

            if(not validate):
                s = 200
                if(speed > 0):
                    s = speed
                    self.servoController.move(
                        servoID, int(coords[0]), s * abs(speedModifier))
        else:
            raise NameError("No valid command found on line: " + str(lineNr))
            
        return 0

    servoAngleMap = {
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.0,
        6: 0.0,
        7: 0.0,
        8: 0.0,
        9: 0.0,
        10: 0.0,
        11: 0.0,
        12: 0.0,
        13: 0.0,
        14: 0.0,
        15: 0.0,
        16: 0.0,
        17: 0.0,
        18: 0.0
    }
    
    legCoordinateMap = {
        1: {0,0,0},
        2: {0,0,0},
        3: {0,0,0},
        4: {0,0,0},
        5: {0,0,0},
        6: {0,0,0}
    }

    # True if we need to get initial positions from servo
    first = True

    def getServoPos(self, x, y, z, legID, speed):
        x += self.LegOffsets[legID][0]
        y += self.LegOffsets[legID][1]
        z += self.LegOffsets[legID][2]
    
        lIK = math.sqrt((self.d + self.lc + x)**2 + y**2)
        dIK = lIK - self.lc
        bIK = math.sqrt((self.e + z)**2 + dIK**2)

        coxaServoId = (legID - 1) * 3 + 1
        femurServoId = (legID - 1) * 3 + 2
        tibiaServoId = (legID - 1) * 3 + 3

        # get previous servo angles
        coxaCurr = self.servoAngleMap[coxaServoId]
        femurCurr = self.servoAngleMap[femurServoId]
        tibiaCurr = self.servoAngleMap[tibiaServoId]

        if (self.first is True):
            self.first = False
            coxaCurr = self.servoController.getPosition(coxaServoId)
            femurCurr = self.servoController.getPosition(femurServoId)
            tibiaCurr = self.servoController.getPosition(tibiaServoId)

        betaIK = math.acos(
            (self.a**2 + self.c**2 - bIK**2) / (2 * self.a * self.c))
        gammaIK = math.acos(
            (self.a**2 + bIK**2 - self.c**2) / (2 * self.a * bIK))
        thetaIK = math.asin(y / lIK)
        tauIK = math.atan((self.e + z) / dIK)

        angleCoxa = thetaIK * (180 / math.pi)
        angleFemur = -90 + ((gammaIK - tauIK) * (180 / math.pi))
        angleTibia = 180 - ((betaIK) * (180 / math.pi))

        if (legID > 1 and legID < 5):
            angleCoxa = -angleCoxa
            angleFemur = -angleFemur
            angleTibia = -angleTibia

        self.servoAngleMap[coxaServoId] = angleCoxa
        self.servoAngleMap[femurServoId] = angleFemur
        self.servoAngleMap[tibiaServoId] = angleTibia

        deltaCoxa = abs(angleCoxa - coxaCurr)
        deltaFemur = abs(angleFemur - femurCurr)
        deltaTibia = abs(angleTibia - tibiaCurr)

        retVal = LegMovement()
        maxDelta = max(deltaCoxa, deltaFemur, deltaTibia)
        retVal.IKCoordinates = {x,y,z}

        if (maxDelta == 0):
            return None

        if (maxDelta == deltaCoxa):
            # print("max delta is coxa")
            retVal.coxaSpeed = speed
            retVal.femurSpeed = int(round(speed * (deltaFemur / maxDelta), 0))
            retVal.tibiaSpeed = int(round(speed * (deltaTibia / maxDelta), 0))
        elif (maxDelta == deltaFemur):
            # print("max delta is femur")
            retVal.coxaSpeed = int(round(speed * (deltaCoxa / maxDelta), 0))
            retVal.femurSpeed = speed
            retVal.tibiaSpeed = int(round(speed * (deltaTibia / maxDelta), 0))
        elif (maxDelta == deltaTibia):
            # print("max delta is tibia")
            retVal.coxaSpeed = int(round(speed * (deltaCoxa / maxDelta), 0))
            retVal.femurSpeed = int(round(speed * (deltaFemur / maxDelta), 0))
            retVal.tibiaSpeed = speed

        # optimal rpm is 114 without load
        timePerAngle = (114.0 * 360.0 / 60.0) * (speed / 1023.0)
        maxExecTime = maxDelta / timePerAngle
        retVal.maxExecTime = maxExecTime

        retVal.coxa = angleCoxa
        if(legID == 1 or legID == 4):
            retVal.coxa += self.offset
        if(legID == 2 or legID == 5):
            retVal.coxa -= self.offset
        retVal.femur = angleFemur
        retVal.tibia = angleTibia
        return retVal
