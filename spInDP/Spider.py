import time
from threading import Thread
from spInDP.RemoteController import RemoteController
from spInDP.ServoController import ServoController
from spInDP.SequenceController import SequenceController
from spInDP.ManualBehavior import ManualBehavior
from spInDP.AutonomeBehavior import AutonomeBehavior
from spInDP.BehaviorType import BehaviorType
from spInDP.WebServer import WebServer
from spInDP.VisionController import VisionController
from spInDP.FindBalloonBehavior import FindBalloonBehavior
from spInDP.AnimationController import AnimationController


class Spider(object):
    """Encapsulates the interaction with the spider."""

    stopLoop = False

    def __init__(self):
        self.remoteController = RemoteController(self)
        self.servoController = ServoController()
        self.sequenceController = SequenceController(self)
        self.animationController = AnimationController(self)
        self.visioncontroller = VisionController()
        self.webserver = WebServer(self)

        self.behavior = ManualBehavior(self.remoteController.Context)
        self.updatethread = None
        self.webserverthread = None

    def start(self):
        print("Starting the spider")
        self.sequenceController.executeStartup()

    def updateLoop(self):
        #60fps update Limit.
        while not self.stopLoop:
            self.behavior.update()
            time.sleep(0.0166667)

    def startUpdateLoopThread(self):
        self.updatethread = Thread(target=self.updateLoop)
        self.updatethread.deamon = True
        self.updatethread.start()

    def startWebserverThread(self):
        self.webserverthread = Thread(target=self.webserver.start)
        self.webserverthread.daemon = True
        self.webserverthread.start()

    def initBehaviorLoop(self):
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
            self.behavior = ManualBehavior(self)
        elif behaviorType == BehaviorType.AutonomeDestroyBalloon:
            print("Switched to find balloon behavior.")
            self.behavior = FindBalloonBehavior(self)

        # Start the loop again
        self.stopLoop = False
        self.startUpdateLoopThread()

    def stop(self):
        self.stopLoop = True
        if (self.updatethread is not None):
            self.updatethread.join()

        self.sequenceController.stop()
        self.remoteController.stop = True
        print("Stopped the spider")
