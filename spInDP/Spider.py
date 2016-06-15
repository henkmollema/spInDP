import time
from threading import Thread

from flask import request

from spInDP.AnimationController import AnimationController
from spInDP.BehaviorType import BehaviorType
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
from spInDP.EmotiveContext import EmotiveContext
from spInDP.EmotiveBehavior import EmotiveBehavior
from spInDP.WebServer import WebServer


class Spider(object):
    """Encapsulates the interaction with the spider."""

    _stopLoop = False
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

        print("Starting the spider...")

        # todo: figure out how to start the spider without wrecking the legs
        # self.sequenceController.executeStartup()

    def updateLoop(self):
        """The logic of the update loop of the spider."""

        while not self._stopLoop:
            self._behavior.update()
            time.sleep(Spider.UPDATE_SLEEP_TIME)

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

    def _shutdownWebserver(self):
        print("Shutdown webserver")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def stop(self):
        """Stops the spider and all its components."""

        self._stopLoop = True
        if self._updateThread is not None:
            self._updateThread.join()

        self._shutdownWebserver()

        self.sequenceController.stop()
        self.remoteController.stop = True
        print("Stopped the spider")
