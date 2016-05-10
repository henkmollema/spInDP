import time
from threading import Thread
from spInDP.RemoteController import RemoteController
from spInDP.ServoController import ServoController
from spInDP.SequenceController import SequenceController
from spInDP.ManualBehavior import ManualBehavior
from spInDP.AutonomeBehavior import AutonomeBehavior
from spInDP.BehaviorType import BehaviorType
from spInDP.WebServer import WebServer

class Spider(object):
    """Encapsulates the interaction with the spider."""

    stopLoop = False

    def __init__(self):
        self.remoteController = RemoteController(self)
        self.servoController = ServoController()
        self.sequenceController = SequenceController(self)
        self.webserver = WebServer(self)

        self.behavior = ManualBehavior(self.remoteController.Context)
        self.updatethread = None
        self.webserverthread = None

    def start(self):
        print("Starting the webserver")
        #self.startWebserverThread()
        self.webserver.start()
        print("Starting the spider")
        self.sequenceController.execute("startup")

    def updateLoop(self):
        # Simulate 60fps update.
        while not self.stopLoop:
            self.behavior.update()
            time.sleep(0.0166667)

    def startUpdateLoopThread(self):
        self.updatethread = Thread(target=self.updateLoop)
        self.updatethread.start()
    
    def startWebserverThread(self):
        self.webserverthread = Thread(target=self.webserver.start)
        self.webserverthread.daemon = True
        self.webserverthread.start()

    def initBevahiorLoop(self):
        print("Initialize the default behavior loop")
        self.startUpdateLoopThread()

    def switchBehavior(self, behaviorType):
        print("SwitchBehavior invoked")

        # Stop the update loop
        self.stopLoop = True
        self.updatethread.join()
        print("Update loop stopped")

        # Switch to the desired behavior
        if behaviorType == BehaviorType.Manual:
            print("Switched to manual behavior")
            self.behavior = ManualBehavior(self.remoteController.Context)
        elif behaviorType == BehaviorType.Autonome:
            print("Autonome behavior not implemented")
            self.behavior = AutonomeBehavior()

        # Start the loop again
        self.stopLoop = False
        self.startUpdateLoopThread()

    def stop(self):
        self.stopLoop = True
        self.updatethread.join()
        print("Stopped the spider")
