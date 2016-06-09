import bluetooth
import threading
import math
from spInDP.RemoteContext import RemoteContext
from spInDP.BehaviorType import BehaviorType


class RemoteController(object):
    """Provides interaction with the physical remote controller over Bluetooth."""

    stop = False
    context = None
    _spider = None
    _sock = None
    _updateLoop = None

    _oldMode = ""
    _oldAction = ""

    def __init__(self, spider):
        """Initializes a new instance of the RemoteController class."""

        self._spider = spider
        self.context = RemoteContext()

        try:
            print("Initializing Bluetooth connection")
            self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self._sock.connect(("20:16:03:30:80:85", 1))
        except BaseException as e:
            print("Initializing bluetooth failed: " + str(e))

        self._updateLoop = threading.Thread(target=self._updateContextLoop)
        self._updateLoop.start()

    def _updateContextLoop(self):
        """The update logic."""

        msg = ""
        while not self.stop:
            try:
                msg += self._sock.recv(1024)
            except BaseException as e:
                print("Error receiving bluetooth data: " + str(e))
                break

            # New line characaters is the end of the message
            msgEnd = msg.find('\n')

            if msgEnd == -1:
                # We have not received a complete message yet,
                # keep reading until we find a \NotImplemented
                continue

            # Read all data until end of message index
            data = msg[:msgEnd]

            # Read joystick position
            xs = data.split(',')
            self.context.jX = float((float(xs[0]) - 512.0) / 512.0)
            self.context.jY = float((float(xs[1]) - 512.0) / 512.0)
            self.context.jZ = float(xs[2])

            self.context.aX = float(xs[3])
            self.context.aY = float(xs[4])

            self.context.jAngle = math.atan2(self.context.jY, self.context.jX) * (180 / math.pi) + 180
            magnitude = math.sqrt((self.context.jX ** 2) + (self.context.jY ** 2))
            self.context.jMagnitude = min(magnitude, 1)

            # Read the mode and action
            mode = xs[5]
            action = xs[6]

            mode = mode.lower().strip()
            action = action.lower().strip()

            if mode != self._oldMode or action != self._oldAction:
                if mode == "limbo":
                    wideWalk = action == "stop"
                    print ("Enable wide walk: " + str(wideWalk))
                    self._spider.animationController.setWideWalking(wideWalk)

                elif mode == "sprint":
                    if action == "start":
                        print ("Start sprint mode")
                    else:
                        print("Stop sprint mode")

                    print ("Sprint not implemented, using walk.")
                    self._spider.animationController.setWideWalking(True)

                elif mode == "gravel":
                    highWalk = action == "start"
                    print ("Set gravel mode: " + str(highWalk))
                    self._spider.animationController.setHighWalking(highWalk)

                elif mode == "spider-gap":
                    if action == "walk":
                        self._spider.animationController.setWideWalking(True)
                    elif action == "horizontal":
                        print ("Keeping body horizontal")
                    elif action == "cross":
                        print ("Cross spider gap")
                    elif action == "touch":
                        print ("Glas aanficken")

                    print("Grind mode not implemented, using walk.")
                    self._spider.animationController.setWideWalking(True)

                elif mode == "vision":
                    if action == "start":
                        self._spider.switchBehavior(BehaviorType.AutonomeDestroyBalloon)
                    else:
                        self._spider.switchBehavior(BehaviorType.Manual)

                elif mode == "fury-road":
                    if action == "start":
                        print ("Start fury road")
                    else:
                        print("Stop fury road")

                    print("Grind mode not implemented, using walk.")
                    self._spider.animationController.setWideWalking(True)

                elif mode == "mating":
                    if action == "start":
                        print("Start mating mode")
                    elif action == "stop":
                        print ("Stop mating mode")
                    elif action == "up":
                        print ("Moving spider up")
                    elif action == "down":
                        print ("Moving spider down")

                    print("Mating not implemented, using walk.")
                    self._spider.animationController.setWideWalking(True)

                # Save current action and messages
                self._oldMode = mode
                self._oldAction = action

            # Continue with next message
            msg = msg[msgEnd + 1:]

        print("Closing socket")
        self._sock.close()
