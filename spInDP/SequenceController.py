import math
import Queue
import time
from spInDP.IKArguments import IKArguments
from spInDP.LegMovement import LegMovement
from spInDP.LegThread import LegThread
from spInDP.SequenceFrame import SequenceFrame


class SequenceController(object):
    """Parses and executes sequence files, also contains the IK calculation"""

    # Based on physical dimensions of scarJo
    a = 11.0  # Femur length (cm)
    c = 16.8  # Tibia (cm)
    e = 5.60  # height (cm)
    d = 12.24  # Horz. afstand van c tot a (cm)
    lc = 4.107  # Lengte coxa (cm)
    b = math.sqrt(e ** 2 + d ** 2)  # diagonal (cm)
    radToDeg = (180 / math.pi)

    anglePerSecond = (
    114.0 * 360.0 / 60.0)  # Optimal rpm is 114 without load at max speed, used to estimate the time it takes to execute an action
    coxaOffset = 45  # Used to offset the coxas from their base position.

    """Maps servosIDs to their current position in degree"""
    servoAngleMap = {
        1: 0.0, 2: 0.0, 3: 0.0,
        4: 0.0, 5: 0.0, 6: 0.0,
        7: 0.0, 8: 0.0, 9: 0.0,
        10: 0.0, 11: 0.0, 12: 0.0,
        13: 0.0, 14: 0.0, 15: 0.0,
        16: 0.0, 17: 0.0, 18: 0.0
    }
    """Maps legIDs to their LegThread"""
    threadMap = {}

    sequenceFrame = None  # Buffer to hold the frame we are building

    def __init__(self, spider):
        """Constructor, initializes the leg threads and legqueues"""
        self.spider = spider
        self.servoController = spider.servoController
        self.legQueue = {}  # Holds the LegMovement objects to be executed by the legs, key is legID
        self.threadMap = {}
        self.stopped = False

        # Initialize a thread and queue per leg
        for x in range(1, 7):
            self.legQueue[x] = Queue.Queue()
            self.threadMap[x] = LegThread(x, self)
            self.threadMap[x].start()

    def stop(self):
        """Stops the LegThreads after the queues are empty"""
        self.stopped = True

        for key in self.threadMap:
            self.threadMap[key].join()

    def getLegCoords(self, legID):
        return self.threadMap[legID].cCoordinates

    def parseSequence(self, filePath, validate=False, speedModifier=1, repeat=1):
        """Sequence file parser, returns the time it takes to execute this sequence in seconds"""

        # print("Parsing sequence at: " + filePath + " repeating for "  + str(repeat))
        with open(filePath, 'r') as f:
            lines = f.readlines()

        totalTime = 0

        words = lines[0].split(' ')
        if (words[0].lower() != "sequence"):
            raise (
                "Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'")
        else:
            if (len(words) > 3):
                self.coxaOffset = int(words[3])
            else:
                self.coxaOffset = 45

        for x in range(0, repeat):
            lineNr = 0

            if (speedModifier < 0):
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
        """Parses a single line of a sequence file and executes the command"""
        if (lineNr == 1 or line.lstrip().startswith("#") or len(line.strip()) == 0):
            return 0

        words = line.split(' ')
        command = words[0].lower().rstrip()
        # print("exec command: " + command)

        # Reverse frames when in a backwards direction
        if (speedModifier < 0):
            if (command == "framebegin"):
                command = "frameend"
            elif (command == "frameend"):
                command = "framebegin"

        if (command == "delay"):
            if (len(words) != 2):
                raise NameError("No argument given for delay at line: " + str(lineNr))

            seconds = float(words[1]) / 1000
            time.sleep(seconds)

        # Wait for all lengs to complete their queued movements
        elif (command == "waitlegs"):
            for key in self.legQueue:
                self.legQueue[key].join()

        # Wait for a single leg to complete its queued movement
        elif (command == "waitleg"):
            if (len(words) != 2):
                raise NameError("Wrong amount of arguments for 'waitleg' command. Expected: 1.")

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
            if (len(words) > 1):
                miliseconds = float(words[1])
                self.sequenceFrame = SequenceFrame(miliseconds)
            else:
                self.sequenceFrame = SequenceFrame()


        elif (command == "frameend"):
            if (self.sequenceFrame is None):
                return 0

            # Put the movements in the frame on the leg queues
            self.addFrameToQueue(self.sequenceFrame)

            # We return the time it takes for this frame to execute
            ret = self.sequenceFrame.maxMaxExecTime

            # Clear the frame so another one can be created on the next framebegin
            self.sequenceFrame.movements.clear()
            self.sequenceFrame = None

            return ret

        # Control legs
        elif (words[0].lower().startswith('l:')):
            if (len(words) < 2 or len(words) > 3):
                raise NameError("Wrong amount of arguments for servo control: " + str(
                    len(words)) + " at line: " + str(lineNr))

            legID = int(words[0].split(':')[1])
            coords = words[1].split(',')
            if (len(coords) != 3):
                raise NameError(
                    "Wrong amount of coords: " + str(len(coords)) + " (expected 3) at line: " + str(lineNr))

            speed = -1
            if (len(words) == 3):
                speed = int(words[2])

            s = 200
            if (speed > 0):
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
                    # Add the movement to the frame we're building
                    self.sequenceFrame.setMovement(legID, legMovement)

        # Control individual servo
        elif (words[0].lower().startswith('s:')):
            if (len(words) < 2 or len(words) > 3):
                raise NameError("Wrong amount of arguments for servo control: " + str(
                    len(words)) + " at line: " + str(lineNr))

            servoID = int(words[0].split(':')[1])
            destinationAngle = float(words[1])

            speed = -1
            if (len(words) == 3):
                speed = int(words[2])
            s = 200
            if (speed > 0):
                s = speed
                self.servoController.move(servoID, int(destinationAngle), s * abs(speedModifier))
                currAngle = self.servoAngleMap[servoID]
                delta = abs(destinationAngle - currAngle)
                self.servoAngleMap[servoID] = destinationAngle
                return delta / (self.anglePerSecond * (speed / 1023.0))




        else:
            raise NameError("No valid command found on line: " + str(lineNr))

        return 0

    first = True  # first = True if we need to get initial positions from servo

    def coordsToLegMovement(self, x, y, z, legID, speed, immediateMode=False):
        """
        Given X Y Z Coordinates this method
        creates and returns a LegMovement object, containing the angles
        and speeds at which the servos need to move.

        It will try to correct the speeds of the servo's
        so they will start and stop moving at the same time

        immediateMode: The speeds won't be corrected
        """

        lIK = math.sqrt((self.d + self.lc + x) ** 2 + y ** 2)
        dIK = lIK - self.lc
        bIK = math.sqrt((self.e + z) ** 2 + dIK ** 2)

        coxaServoId = (legID - 1) * 3 + 1
        femurServoId = (legID - 1) * 3 + 2
        tibiaServoId = (legID - 1) * 3 + 3

        # get previous servo angles
        coxaCurr = self.servoAngleMap[coxaServoId]
        femurCurr = self.servoAngleMap[femurServoId]
        tibiaCurr = self.servoAngleMap[tibiaServoId]

        # If the servomap is empty try to read the position directly from the servo
        if (self.first is True):
            self.first = False
            coxaCurr = self.servoController.getPosition(coxaServoId)
            femurCurr = self.servoController.getPosition(femurServoId)
            tibiaCurr = self.servoController.getPosition(tibiaServoId)

        betaIK = math.acos(
            (self.a ** 2 + self.c ** 2 - bIK ** 2) / (2 * self.a * self.c))
        gammaIK = math.acos(
            (self.a ** 2 + bIK ** 2 - self.c ** 2) / (2 * self.a * bIK))
        thetaIK = math.asin(y / lIK)
        tauIK = math.atan((self.e + z) / dIK)

        angleCoxa = thetaIK * self.radToDeg
        angleFemur = -90 + ((gammaIK - tauIK) * self.radToDeg)
        angleTibia = 180 - ((betaIK) * self.radToDeg)

        if (legID > 1 and legID < 5):
            angleCoxa = -angleCoxa
            angleFemur = -angleFemur
            angleTibia = -angleTibia

        if (legID == 1 or legID == 4):
            angleCoxa += self.coxaOffset
        if (legID == 2 or legID == 5):
            angleCoxa -= self.coxaOffset

        self.servoAngleMap[coxaServoId] = angleCoxa
        self.servoAngleMap[femurServoId] = angleFemur
        self.servoAngleMap[tibiaServoId] = angleTibia

        # Create a LegMovement object
        deltaCoxa = abs(angleCoxa - coxaCurr)
        deltaFemur = abs(angleFemur - femurCurr)
        deltaTibia = abs(angleTibia - tibiaCurr)

        retVal = LegMovement()
        maxDelta = max(deltaCoxa, deltaFemur, deltaTibia)

        if (maxDelta == 0):
            return None

        # If we are in immediate mode, don't calculate delta's
        if (not immediateMode):
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
        else:
            retVal.coxaSpeed = speed
            retVal.femurSpeed = speed
            retVal.tibiaSpeed = speed

        retVal.coxa = angleCoxa
        retVal.femur = angleFemur
        retVal.tibia = angleTibia

        retVal.IKCoordinates = [x, y, z]
        return retVal

    def addFrameToQueue(self, frame):
        """
            Add the movements in a SequenceFrame to the legQueues
            So they will be executed when it's their turn
        """

        scaledMovements = frame.getScaledMovements()
        for x in range(1, 7):
            mov = scaledMovements.get(x, None)
            # Create an 'empty movement
            if (mov is None):
                mov = LegMovement()
                mov.empty = True
                mov.maxExecTime = frame.maxMaxExecTime

            self.legQueue[x].put(mov)


    def setFrame(self, frame):
        """
            Immediately sends the servos to the LegMovements
            in a given SequenceFrame
        """

        if (self.legQueueIsEmpty()):
            scaledMovements = frame.getScaledMovements()
            for x in scaledMovements:
                self.servoController.move((x - 1) * 3 + 1, scaledMovements[x].coxa, scaledMovements[x].coxaSpeed)
                self.servoController.move((x - 1) * 3 + 2, scaledMovements[x].femur, scaledMovements[x].femurSpeed)
                self.servoController.move((x - 1) * 3 + 3, scaledMovements[x].tibia, scaledMovements[x].tibiaSpeed)
        else:
            print("setFrame() failed, legQueues not empty")

    def legQueueIsEmpty(self):
        """
            Returns true if no LegMovements are on the LegQueues
        """
        for x in range(1, 7):
            if (not self.legQueue[x].empty()):
                return False
        return True

    def legQueueSize(self):
        max = 0
        for x in range(1, 7):
            max = max(self.legQueue[x].qsize(), max)

        return max

