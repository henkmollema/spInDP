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
        

