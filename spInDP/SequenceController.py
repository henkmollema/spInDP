import time

class SequenceController(object):
    """Executes sequences using servos."""

    def __init__(self, spider):
        self.spider = spider
        self.servoController = spider.servoController

    def execute(self, sequenceName):
        print("Executing sequence: " + sequenceName)
        
        if sequenceName == "startup":
            self.executeStartup()

    def executeStartup(self):
        print("Executing startup sequence")

        """

                   V 120
          /\  O_o /\
         /  \____/  \
        /        ^   \
                 -65

        """

        self.servoController.move(10, -100)
        time.sleep(0.5)
        self.servoController.move(10, 0)
        time.sleep(0.5)
        self.servoController.move(10, 100)

        #self.servoController.move(17, -65)
        #self.servoController.move(18, 120, speed=512)
                
        # for x in range(0, 3):
        #     self.servoController.move(16, -25)
        #     self.servoController.move(17, 0)
        #     self.servoController.move(18, 0, speed=512)
            
        #     time.sleep(0.5)
            
        #     self.servoController.move(16, 25)
        #     self.servoController.move(17, -65)
        #     self.servoController.move(18, 120, speed=512)
        
        # self.servoController.move(16, 0)
        # self.servoController.move(17, -65)
        # self.servoController.move(18, 120, speed=512)
        
	def parseSequence(self, filePath):
        print("Parsing sequence at: " + filePath)
        f = open(filePath, 'r')
		hasHeader = False;
		lineNr = 0
		
		for line in f:
			words = line.split(' ');
			if(!hasHeader && words[0].lower() != "sequence"):
				raise("Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'")
			else
				hasHeader = True
				continue
				
			if(words[0].lower() == "delay"):
				if(len(words) != 2):
					raise("No argument given for delay at line: " + lineNr)
				time.sleep(int(word[1]) / 1000)
				
			if(words[0].lower().startswith('s')):
				if(len(words) < 2 || len(words) > 3):
					raise("Wrong amount of arguments for servo control: " + len(words) + " at line: " + lineNr)
					
				servoID = int(words[0].split(':')[1]);
				coords = words[1].split(',');
				if(len(coords) != 3):
					raise("Wrong amount of coords: "+len(coords)+" at line: " + lineNr)
				
				speed = -1
				if(len(words) == 3):
					speed = int(words[2])
				
				#
				#
				#hier de servocontroller aanroepen met de variabelen
				#
				#
				
			
			lineNr++
