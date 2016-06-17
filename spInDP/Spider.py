import time
from threading import Thread
import RPi.GPIO as GPIO

from spInDP.AnimationController import AnimationController
from spInDP.BehaviorType import BehaviorType
from spInDP.EmotiveBehavior import EmotiveBehavior
from spInDP.EmotiveContext import EmotiveContext
from spInDP.FindBalloonBehavior import FindBalloonBehavior
from spInDP.FollowBalloonBehavior import FollowBalloonBehavior
from spInDP.FuryRoadBehavior import FuryRoadBehavior
from spInDP.ImmediateBehavior import ImmediateBehavior
from spInDP.ManualBehavior import ManualBehavior
from spInDP.ManualHorizontalBehavior import ManualHorizontalBehavior
from spInDP.PushBehavior import PushBehavior
from spInDP.RemoteController import RemoteController
from spInDP.SensorDataProvider import SensorDataProvider
from spInDP.SequenceController import SequenceController
from spInDP.ServoController import ServoController
from spInDP.SprintBehavior import SprintBehavior
from spInDP.TouchBehavior import TouchBehavior
from spInDP.VisionController import VisionController
from spInDP.WebServer import WebServer


class Spider(object):
    """Encapsulates the interaction with the spider."""

    _stopLoop = False
    _server = None
    UPDATE_SLEEP_TIME = 0.008

    def __init__(self):
        """Initializes the spider."""

        # Public fields
        self.servoController = ServoController()
        self.sensorDataProvider = SensorDataProvider()
        self.sequenceController = SequenceController(self)
        self.animationController = AnimationController(self)
        self.visioncontroller = VisionController()
        self.webserver = WebServer(self)
        self.remoteController = RemoteController(self)
        self.emotiveContext = EmotiveContext()

        # Private fields
        self._behavior = ManualBehavior(self)
        self._updateThread = None
        self._webserverThread = None

    def start(self):
        """Starts the spider."""

        print ("Turn on LEDs")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(10, GPIO.OUT)
        GPIO.output(10, GPIO.HIGH)

        print("Starting the spider...")
        time.sleep(self.sequenceController.parseSequence('sequences/startup.txt'))

    def updateLoop(self):
        """The logic of the update loop of the spider."""

        while not self._stopLoop:
            self._behavior.update()
            time.sleep(Spider.UPDATE_SLEEP_TIME)

        print("Stopped the update loop")

    def _startUpdateLoopThread(self):
        """Starts the update loop in a seperate thread."""

        self._updateThread = Thread(target=self.updateLoop)
        self._updateThread.deamon = True
        self._updateThread.start()

    def startWebserverThread(self):
        """Starts the webserver in a seperate thread."""

        self._webserverThread = Thread(target=self.webserver.start)
        self._webserverThread.daemon = True
        self._webserverThread.start()

    def initBehaviorLoop(self):
        """Initializes the default behavior loop of the spider."""

        print("Initialize the default behavior loop")
        self._startUpdateLoopThread()

    def switchBehavior(self, behaviorType):
        """Switches the active behavior of the spider."""

        if self._updateThread is None:
            return

        print("SwitchBehavior invoked: " + behaviorType)

        # Stop the update loop
        self._stopLoop = True
        self._updateThread.join()

        # Switch to the desired behavior
        if behaviorType == BehaviorType.Manual:
            print("Switched to manual behavior")
            self._behavior = ManualBehavior(self)

        elif behaviorType == BehaviorType.ManualHorizontal:
            print("Switched to manual horizontal behavior")
            self._behavior = ManualHorizontalBehavior(self)

        elif behaviorType == BehaviorType.AutonomeDestroyBalloon:
            print("Switched to destroy balloon behavior.")
            self._behavior = FindBalloonBehavior(self)

        elif behaviorType == BehaviorType.AutonomeFollowBalloon:
            print("Switched to follow balloon behavior.")
            self._behavior = FollowBalloonBehavior(self)

        elif behaviorType == BehaviorType.AutonomeFuryRoad:
            print("Switched to autonome fury road behavior")
            self._behavior = FuryRoadBehavior(self)

        elif behaviorType == BehaviorType.Immediate:
            print("Switched to immediate behavior.")
            self._behavior = ImmediateBehavior(self)

        elif behaviorType == BehaviorType.Push:
            print("Switched to push behavior.")
            self._behavior = PushBehavior(self)

        elif behaviorType == BehaviorType.Touch:
            print("Switched to touch behavior.")
            self._behavior = TouchBehavior(self)

        elif behaviorType == BehaviorType.Sprint:
            print("Switched to sprint behavior")
            self._behavior = SprintBehavior(self)

        elif behaviorType == BehaviorType.Emotive:
            print("Switched to emotive behavior")
            self._behavior = EmotiveBehavior(self)

        # Start the loop again
        self._stopLoop = False
        self._startUpdateLoopThread()

    def stop(self):
        """Stops the spider and all its components."""

        self.remoteController.stop = True
        self._stopLoop = True
        if self._updateThread is not None:
            self._updateThread.join()

        self.sequenceController.stop()

    def shutdown(self):
        """Stops the spider and shuts down the RPi."""

        self.stop()
        import os
        os.system("sudo shutdown -h now")
