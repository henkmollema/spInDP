import math
import Queue
import time
from spInDP.IKArguments import IKArguments
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
    radToDeg = (180 / math.pi)

    # optimal rpm is 114 without load at max speed
    anglePerSecond = (114.0 * 360.0 / 60.0)

    coxaOffset = 45

    servoAngleMap = {
        1: 0.0, 2: 0.0, 3: 0.0,
        4: 0.0, 5: 0.0, 6: 0.0,
        7: 0.0, 8: 0.0, 9: 0.0,
        10: 0.0, 11: 0.0, 12: 0.0,
        13: 0.0, 14: 0.0, 15: 0.0,
        16: 0.0, 17: 0.0, 18: 0.0
    }

    sequenceFrame = None

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
        return self.parseSequence("sequences/pre-stab-left.txt", repeat=1, speedModifier=1)
        
    def executeStabLeft(self):
        return self.parseSequence("sequences/stab-left.txt", repeat=1, speedModifier=1)
        
    def executePostStabLeft(self):
        return self.parseSequence("sequences/post-stab-left.txt", repeat=1, speedModifier=1)
        
    def executePreStabRight(self):
        self.parseSequence("sequences/pre-stab-right.txt", repeat=1, speedModifier=1)
        
    def executeStabRight(self):
        self.parseSequence("sequences/stab-right.txt", repeat=1, speedModifier=1)
        
    def executePostStabRight(self):
        self.parseSequence("sequences/post-stab-right.txt", repeat=1, speedModifier=1)

    def executeStartup(self):
        return self.parseSequence("sequences/startup.txt")

    #Returns the time it takes to execute this sequence in seconds
    def parseSequence(self, filePath, validate=False, speedModifier=1, repeat=1):
        #print("Parsing sequence at: " + filePath + " repeating for "  + str(repeat))

        with open(filePath, 'r') as f:
            lines = f.readlines()

        totalTime = 0
        
        words = lines[0].split(' ')
        if (words[0].lower() != "sequence"):
            raise(
                "Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'")
        else:
            if(len(words) > 3):
                self.coxaOffset = int(words[3])
            else:
                self.coxaOffset = 45

        for x in range(0, repeat):
            lineNr = 0

            if(speedModifier < 0):
                lineNr = len(lines)
                for line in reversed(lines):
                    totalTime += self.interpretLine(line, lineNr, speedModifier)
                    lineNr -= 1
            else:
                lineNr = 1
                for line in lines:
                    totalTime += self.interpretLine(line, lineNr, speedModifier)
                    lineNr += 1
        
        return totalTime
        
    def interpretLine(self, line, lineNr, speedModifier=1):
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
            #for x in range(1, 7):
                ## Create an 'empty movement
               # mov = LegMovement()
               # mov.empty = True
               # mov.maxExecTime = seconds
                ##Put an empty legmovement with delay as exectime in the leg queue
               # self.legQueue[x].put(mov)
               # return seconds 
            time.sleep(seconds)

        # Wait for all lengs to complete their queued movements
        elif (command == "waitlegs"):
            for key in self.legQueue:
                self.legQueue[key].join()

        # Wait for a single leg to complete its queued movement
        elif (command == "waitleg"):
            if (len(words) != 2):
                raise NameError(                    "Wrong amount of arguments for 'waitleg' command. Expected: 1.")

            legId = int(words[1])

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
            print("Including sequence: " + seq)
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

            #Put the movements in the frame on the leg queues
            scaledMovements = self.sequenceFrame.getScaledMovements()
            for x in range(1, 7):
                mov = scaledMovements.get(x, None)

                # Create an 'empty movement
                if (mov is None):
                    mov = LegMovement()
                    mov.empty = True
                    mov.maxExecTime = self.sequenceFrame.maxMaxExecTime
                #Here we put the legmovement object from the frame(or an empty one) in the leg queue
                self.legQueue[x].put(mov)

            #We return the time it takes for this frame to execute
            ret = self.sequenceFrame.maxMaxExecTime

            #Clear the frame so another one can be created on the next framebegin
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

            s = 200
            if(speed > 0):
                s = speed

                ikArgs = IKArguments()
                ikArgs.x = float(coords[0])
                ikArgs.y = float(coords[1])
                ikArgs.z = float(coords[2])
                ikArgs.legID = legID
                ikArgs.speed = s * abs(speedModifier)

                legMovement = self.coordsToLegMovement(ikArgs.x, ikArgs.y, ikArgs.z, ikArgs.legID, ikArgs.speed);

                if (legMovement is None):
                    return 0

                if (self.sequenceFrame is None):
                    self.legQueue[legID].put(legMovement)
                else:
                    #Add the movement to the frame we're building
                    self.sequenceFrame.setMovement(legID, legMovement)

        # Control individual servo
        elif(words[0].lower().startswith('s:')):
            if(len(words) < 2 or len(words) > 3):
                raise NameError("Wrong amount of arguments for servo control: " + str(
                    len(words)) + " at line: " + str(lineNr))

            servoID = int(words[0].split(':')[1])
            destinationAngle = float(words[1])

            speed = -1
            if(len(words) == 3):
                speed = int(words[2])
            s = 200
            if(speed > 0):
                s = speed
                self.servoController.move(servoID, int(destinationAngle), s * abs(speedModifier))
                currAngle = self.servoAngleMap[servoID]
                delta = abs(destinationAngle - currAngle)
                self.servoAngleMap[servoID] = destinationAngle
                return delta / (self.anglePerSecond * (speed / 1023.0))




        else:
            raise NameError("No valid command found on line: " + str(lineNr))
            
        return 0

    #Returns a LegMovement Object.
    # True if we need to get initial positions from servo
    first = True
    def coordsToLegMovement(self, x, y, z, legID, speed):    
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

        #If the servomap is empty try to read the position directly from the servo
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

        angleCoxa = thetaIK * self.radToDeg
        angleFemur = -90 + ((gammaIK - tauIK) * self.radToDeg)
        angleTibia = 180 - ((betaIK) * self.radToDeg)

        if (legID > 1 and legID < 5):
            angleCoxa = -angleCoxa
            angleFemur = -angleFemur
            angleTibia = -angleTibia

        self.servoAngleMap[coxaServoId] = angleCoxa
        self.servoAngleMap[femurServoId] = angleFemur
        self.servoAngleMap[tibiaServoId] = angleTibia

        #Create a LegMovement object
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

        maxExecTime = maxDelta / (self.anglePerSecond * (speed / 1023.0))
        retVal.maxExecTime = maxExecTime

        retVal.coxa = angleCoxa
        if(legID == 1 or legID == 4):
            retVal.coxa += self.coxaOffset
        if(legID == 2 or legID == 5):
            retVal.coxa -= self.coxaOffset
        retVal.femur = angleFemur
        retVal.tibia = angleTibia
        return retVal


