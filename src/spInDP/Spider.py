import time
from threading import Thread
from RemoteController import RemoteController
from ServoController import ServoController
from SequenceController import SequenceController
from ManualBehavior import ManualBehavior
from AutonomeBehavior import AutonomeBehavior
from BehaviorType import BehaviorType

class Spider(object):
    """Encapsulates the interaction with the spider."""

    stopLoop = False

    def __init__(self):
        self.remoteController = RemoteController(self)
        self.servoController = ServoController()
        self.sequenceController = SequenceController(self)

        self.behavior = (self.remoteController.Context)
        self.thread = None

    def start(self):
        print("Starting the spider")
        self.sequenceController.execute("startup")

    def updateLoop(self):
        # Simulate 60fps update.
        while not self.stopLoop:
            self.behavior.update()
            time.sleep(0.0166667)

    def startUpdateLoopThread(self):
        self.thread = Thread(target=self.updateLoop)
        self.thread.start()

    def initBevahiorLoop(self):
        print("Initialize the default behavior loop")
        self.startUpdateLoopThread()

    def switchBehavior(self, behaviorType):
        print("SwitchBehavior invoked")

        # Stop the update loop
        self.stopLoop = True
        self.thread.join()
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
        self.thread.join()
        print("Stopped the spider")
