import time
import math
import threading
import Queue
from spInDP.LegVector import LegVector

class LegThread(threading.Thread):
    def __init__(self, legId, sequenceController, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(LegThread, self).__init__()
        self.target = target
        self.name = name
        self.legId = legId
        self.sequenceController = sequenceController
        return
        
    def run(self):
        q = self.sequenceController.legQueue[self.legId]
        while True:        
            if not q.empty():                
                vLeg = q.get()
                print("got instr: " + str(vLeg)+ str(q.qsize()) + ", items in queue")
                
                self.sequenceController.servoController.move((self.legId - 1) * 3 + 1, vLeg.coxa, vLeg.coxaSpeed)
                self.sequenceController.servoController.move((self.legId - 1) * 3 + 2, vLeg.femur, vLeg.femurSpeed)
                self.sequenceController.servoController.move((self.legId - 1) * 3 + 3, vLeg.tibia, vLeg.tibiaSpeed)
                
                time.sleep(vLeg.maxExecTime)
                
                #time.sleep(0.001)
        return

class SequenceController(object):
    """Parses and executes sequences using servos."""

    # Based on physical dimensions of scarJo
    a = 11.0  # Femur length (cm)
    c = 15.0  # Tibia (cm)
    e = 5.60  # height (cm)
    d = 12.24  # Horz. afstand van c tot a (cm)
    lc = 4.107  # Lengte coxa (cm)
    b = math.sqrt(e**2 + d**2)  # diagonal (cm)
    
    def __init__(self, spider):
        self.spider = spider
        self.servoController = spider.servoController
        self.legQueue = {
            1: Queue.Queue(),
            2: Queue.Queue(),
            3: Queue.Queue(),
            4: Queue.Queue(),
            5: Queue.Queue(),
            6: Queue.Queue()
        }
        self.threadMap = {
            1: LegThread(1, self, name = 'legthread'),
            2: LegThread(2, self, name = 'legthread'),
            3: LegThread(3, self, name = 'legthread'),
            4: LegThread(4, self, name = 'legthread'),
            5: LegThread(5, self, name = 'legthread'),
            6: LegThread(6, self, name = 'legthread')
        }
        
        self.threadMap[1].deamon = True
        self.threadMap[2].deamon = True
        self.threadMap[3].deamon = True
        self.threadMap[4].deamon = True
        self.threadMap[5].deamon = True
        self.threadMap[6].deamon = True
        
        self.threadMap[1].start()
        self.threadMap[2].start()
        self.threadMap[3].start()
        self.threadMap[4].start()
        self.threadMap[5].start()
        self.threadMap[6].start()

    def execute(self, sequenceName):
        print("Executing sequence: " + sequenceName)

        if sequenceName == "startup":
            # self.executeServosTest()
            self.executeWalk()
            self.executeStartup()

    def executeServosTest(self):
        print("Execute servos test")
        self.parseSequence("sequences/test-all-servo2.txt")

    def executeWalk(self):
        print("Execute walk")
        self.parseSequence("sequences/walk.txt", repeat=5)

    def executeCrawl(self):
        print("Execute crawl")
        self.parseSequence("sequences/crawl.txt", repeat=4)

    def executeStartup(self):
        print("Executing startup sequence")
        self.parseSequence("sequences/startup.txt")

    def parseSequence(self, filePath, validate=False, repeat=1):
        print("Parsing sequence at: " + filePath)

        for x in range(0, repeat):
            lineNr = 0

            with open(filePath, 'r') as f:
                for line in f:
                    lineNr += 1

                    if(line.lstrip().startswith("#")):
                        continue

                    words = line.split(' ')
                    command = words[0].lower()
                    if (lineNr == 0 and words[0].lower() != "sequence"):
                        raise(
                            "Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'")
                    elif (lineNr == 0):
                        continue

                    if(command == "delay"):
                        if(len(words) != 2):
                            raise NameError(
                                "No argument given for delay at line: " + str(lineNr))

                        seconds = float(words[1]) / 1000

                        if(not validate):
                            #print("Will delay " + str(seconds) + " seconds")
                            time.sleep(seconds)

                    if (command == "waitleg"):
                        if (len(words) != 2):
                            raise NameError(
                                "Wrong amount of arguments for 'waitleg' command. Expected: 1.")

                        legId = int(words[1])
                        #print("waiting for movement of leg " + str(legId) + " to finish")
                        self.waitForLeg(legId)

                    if (command == "print"):
                        if (len(words) < 2):
                            raise NameError("Nothing to print")

                        print(' '.join(words[1:])[:-1])

                    # Control legs
                    if(words[0].lower().startswith('l:')):
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
                            #print("Will control leg {0}, coords: {1}, speed: {2}".format(legID, coords, speed))
                            s = 200
                            if(speed > 0):
                                s = speed

                            # try:
                                vLeg = self.getServoPos(float(coords[0]), float(coords[1]), float(coords[2]), legID, s)
                                    
                                if (vLeg is None):
                                    return
                                    
                                self.legQueue[legID].put(vLeg)
                                    
                                #self.servoController.move((legID - 1) * 3 + 1, vLeg.coxa, vLeg.coxaSpeed)
                                #self.servoController.move((legID - 1) * 3 + 2, vLeg.femur, vLeg.femurSpeed)
                                #self.servoController.move((legID - 1) * 3 + 3, vLeg.tibia, vLeg.tibiaSpeed)
                                    
                                #print("sleeping for: " + str(vLeg.maxExecTime))
                                #time.sleep(vLeg.maxExecTime)
                            # except:
                                #print("Error on line: " + str(lineNr))

                    # Control individual servo
                    if(words[0].lower().startswith('s:')):
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
                            #print("Will control servo {0}, coords: {1}, speed: {2}".format(servoID, coords, speed))
                            s = 200
                            if(speed > 0):
                                s = speed

                            # try:
                                self.servoController.move(
                                    servoID, int(coords[0]), s)
                            # except:
                                #print("Error on line: " + str(lineNr))

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

     # True if we need to get initial positions from servo
    first = True

    def getServoPos(self, x, y, z, legID, speed):
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
        
        #print("current positions: " + str(coxaCurr) + ", " + str(femurCurr) + ", " + str(tibiaCurr))        
        
        betaIK = math.acos((self.a**2 + self.c**2 - bIK**2) / (2 * self.a * self.c))
        gammaIK = math.acos((self.a**2 + bIK**2 - self.c**2) / (2 * self.a * bIK)) 
        thetaIK = math.asin(y / lIK)
        tauIK = math.atan((self.e + z) / dIK)
        
        angleCoxa = thetaIK * (180 / math.pi)
        angleFemur = -90 + ((gammaIK - tauIK) * (180 / math.pi))
        angleTibia = 180 - ((betaIK) * (180 / math.pi))        
        #print ("angle tibia :" +str(angleTibia) +", tauIK: " + str(tauIK))
        
        self.servoAngleMap[coxaServoId] = angleCoxa
        self.servoAngleMap[femurServoId] = angleFemur
        self.servoAngleMap[tibiaServoId] = angleTibia

        deltaCoxa = abs(angleCoxa - coxaCurr)
        deltaFemur = abs(angleFemur - femurCurr)
        deltaTibia = abs(angleTibia - tibiaCurr)
        #print("deltas " + str(deltaCoxa) + ", " + str(deltaFemur) + ", " + str(deltaTibia))

        retVal = LegVector()
        maxDelta = max(deltaCoxa, deltaFemur, deltaTibia)
        
        if (maxDelta == 0):
            return None
        
        if (maxDelta == deltaCoxa):
            #print("max delta is coxa")            
            retVal.coxaSpeed = speed
            retVal.femurSpeed = int(round(speed * (deltaFemur / maxDelta), 0))
            retVal.tibiaSpeed = int(round(speed * (deltaTibia / maxDelta), 0))
        elif (maxDelta == deltaFemur):
            #print("max delta is femur")
            retVal.coxaSpeed = int(round(speed * (deltaCoxa / maxDelta), 0))
            retVal.femurSpeed = speed
            retVal.tibiaSpeed = int(round(speed * (deltaTibia / maxDelta), 0))
        elif (maxDelta == deltaTibia):
            #print("max delta is tibia")
            retVal.coxaSpeed = int(round(speed * (deltaCoxa / maxDelta), 0))
            retVal.femurSpeed = int(round(speed * (deltaFemur / maxDelta), 0))
            retVal.tibiaSpeed = speed

        # optimal rpm is 114 without load
        timePerAngle = (114.0 * 360.0 / 60.0) * (speed / 1023.0)
        maxExecTime = maxDelta / timePerAngle  
        retVal.maxExecTime = maxExecTime

        #print("angleCoxa: " + str(angleCoxa))
        #print("angleFemur: " + str(angleFemur))
        #print("angleTibia: " + str(angleTibia))

        retVal.coxa = angleCoxa
        retVal.femur = angleFemur
        retVal.tibia = angleTibia
        return retVal

    def sleepForLeg(self, execTime):
        time.sleep(execTime)

    def waitForLeg(self, legId):
        coxaServoId = (legId - 1) * 3 + 1
        femurServoId = (legId - 1) * 3 + 2
        tibiaServoId = (legId - 1) * 3 + 3

        while (self.servoController.isMoving(coxaServoId) or
               self.servoController.isMoving(femurServoId) or
               self.servoController.isMoving(tibiaServoId)):
            # print(pos)
            time.sleep(0.004)

        print("finished moving")
        return
