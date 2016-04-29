import time

class SequenceController(object):
    """Executes sequences using servos."""

    def __init__(self, spider):
        self.spider = spider
        self.servoController = spider.servoController

    def execute(self, sequenceName):
        print("Executing sequence: " + sequenceName)
        
        if sequenceName == "startup":
            #self.executeServosTest()
            self.executeWalk()
            self.executeStartup()
            
    def executeServosTest(self):
        print("Execute servos test")
        self.parseSequence("sequences/test-all-servo.txt")
        
    def executeWalk(self):
        print("Execute walk")
        self.parseSequence("sequences/walk.txt", repeat=6)        

    def executeStartup(self):
        print("Executing startup sequence")
        self.parseSequence("sequences/startup.txt")
        
    def parseSequence(self, filePath, validate=False, repeat=1):
        print("Parsing sequence at: " + filePath)
                
        for x in range(0, repeat):        
            hasHeader = False
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
                        
                    if(words[0].lower().startswith('s:')):
                        if(len(words) < 2 or len(words) > 3):
                            raise NameError("Wrong amount of arguments for servo control: " + str(len(words)) + " at line: " + str(lineNr))
                            
                        servoID = int(words[0].split(':')[1]);
                        coords = words[1].split(',');
                        if(len(coords) != 3):
                            raise NameError("Wrong amount of coords: "+str(len(coords))+" at line: " + str(lineNr))
                        
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
                            #hier de servocontroller aanroepen met de variabelen wanneer not validate

