import time
from spInDP.LegVector import LegVector



class SequenceController(object):
    """Executes sequences using servos."""
    
    ## Based on physical dimensions of scarJo
    a = 11 #Femur length (cm)
    c = 15 #Tibia (cm)
    e = 6.85 #height (cm)
    d = 12.24 #Horz. afstand van c tot a (cm)
    lc = 4.107 #Lengte coxa (cm)
    b = math.sqrt(e**2 + d**2) #diagonal (cm)

    def __init__(self, spider):
        self.spider = spider
        self.servoController = spider.servoController

    def execute(self, sequenceName):
        print("Executing sequence: " + sequenceName)
        
        if sequenceName == "startup":
            self.executeServosTest()
            self.executeWalk()
            self.executeCrawl()
            self.executeStartup()
            
    def executeServosTest(self):
        print("Execute servos test")
        self.parseSequence("sequences/test-all-servo2.txt")
        
    def executeWalk(self):
        print("Execute walk")
        self.parseSequence("sequences/walk.txt", repeat=4)
        
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
                    words = line.split(' ')
                    if (lineNr == 0 and words[0].lower() != "sequence"):
                        raise("Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'")
                    elif (lineNr == 0):
                        continue

                    if(words[0].lower() == "delay"):
                        if(len(words) != 2):
                            raise NameError("No argument given for delay at line: " + str(lineNr))
                        seconds = float(words[1]) / 1000
                        
                        if(not validate):
                            print("Will delay " + str(seconds) + " seconds")
                            time.sleep(seconds)
                    
                    #Control legs
                    if(words[0].lower().startswith('l:')):
                        if(len(words) < 2 or len(words) > 3):
                            raise NameError("Wrong amount of arguments for servo control: " + str(len(words)) + " at line: " + str(lineNr))
                            
                        legID = int(words[0].split(':')[1]);
                        coords = words[1].split(',')[0];
                        if(len(coords) != 3):
                            raise NameError("Wrong amount of coords: "+str(len(coords))+" (expected 3) at line: " + str(lineNr))
                        
                        speed = -1
                        if(len(words) == 3):
                            speed = int(words[2])

                        if(not validate):
                            print("Will control servo {0}, coords: {1}, speed: {2}".format(servoID, coords, speed) )
                            s = 200
                            if(speed > 0):
                                s = speed
                            
                            try:
                                vLeg = self.getServoPos(float(coords[0]), float(coords[1]), float(coords[2]))
                                self.servoController.move((legID - 1) * 3 + 1, vLeg.coxa, s)
                                self.servoController.move((legID - 1) * 3 + 2, vLeg.femur, s)
                                self.servoController.move((legID - 1) * 3 + 3, vLeg.tibia, s)
                            except:
                                print("Error on line: " + str(lineNr))    
                        
                    
                    #Control individual servo
                    if(words[0].lower().startswith('s:')):
                        if(len(words) < 2 or len(words) > 3):
                            raise NameError("Wrong amount of arguments for servo control: " + str(len(words)) + " at line: " + str(lineNr))
                            
                        servoID = int(words[0].split(':')[1]);
                        coords = words[1].split(',')[0];
                        if(len(coords) != 1):
                            raise NameError("Wrong amount of coords: "+str(len(coords))+" (expected 1) at line: " + str(lineNr))
                        
                        speed = -1
                        if(len(words) == 3):
                            speed = int(words[2])

                        if(not validate):
                            print("Will control servo {0}, coords: {1}, speed: {2}".format(servoID, coords, speed) )
                            s = 200
                            if(speed > 0):
                                s = speed
                            
                            try:
                                self.servoController.move(servoID, int(coords[0]), s)
                            except:
                                print("Error on line: " + str(lineNr))
                            

    def getServoPos(self, x,y,z):
        lIK = math.sqrt((self.d+self.lc+x)**2+y**2)
        dIK = lIK - self.lc
        bIK = sqrt((self.e+z)**2 + dIK**2)
    
        alphaIK = acos(bIK**2 + self.c**2 - self.a**2) / (2*bIK*self.c)
        betaIK  = acos(self.a**2 + self.c**2 -bIK**2) / (2*self.a*self.c)
        gammaIK = acos(self.a**2 + bIK**2 - self.c**2) / (2 * self.a * bIK)
        thetaIK = asin(y/lIK)
        tauIK   = atab(self.e/dIK)
    
        angleCoxa = thetaIK * (180/math.pi)
        angleFemur = (alphaIK - tauIK) * (180/math.pi)
        angleTibia = (betaIK) * (180/math.pi)

        retVal = LegVector()
        retval.coxa = 180 - angleCoxa
        retVal.femur = 180 - angleFemur
        retVal.tibia = 180 - angleTibia
        return retVal
