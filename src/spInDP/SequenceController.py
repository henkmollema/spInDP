class SequenceController(object):
    """Executes sequences using servos."""

    def __init__(self, spider):
        self.spider = spider
        self.servoController = spider.servoController

    def execute(self, sequenceName):
        print("Executing sequence: " + sequenceName)
        print("Servo temp: " + self.servoController.getTemp(17))

        if sequenceName == "startup":
            self.executeStartup()

    def executeStartup(self):
        print("Executing startup sequence")

        self.servoController.write(17, 90)

