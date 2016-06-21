import math
import threading
import time

import bluetooth

from spInDP.BehaviorType import BehaviorType
from spInDP.RemoteContext import RemoteContext


class RemoteController(object):
    """Provides interaction with the physical remote controller over Bluetooth."""

    stop = False
    context = None

    _spider = None
    _socket = None
    _updateLoop = None
    _oldMode = ""
    _oldAction = ""

    def __init__(self, spider):
        """Initializes a new instance of the RemoteController class."""

        self._spider = spider
        self.context = RemoteContext()

        print("Initializing Bluetooth connection")
        self._tryConnect()

        self._updateLoop = threading.Thread(target=self._updateContextLoop)
        self._updateLoop.start()

    def _tryConnect(self):
        """Attempts to connect the socket with the the Arduino using Bluetooth."""

        tries = 0
        maxTries = 10
        connected = False
        ex = None

        while tries <= maxTries:
            try:
                self._socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                # self._socket.settimeout(5.0)
                self._socket.connect(("20:16:03:30:80:85", 1))
                connected = True
                print ("Connected to Bluetooth")
                break
            except BaseException as e:
                print("Bluetooth connection failed. Retrying..." + str(e))
                tries += 1
                ex = e
                time.sleep(1)
                continue

        if not connected:
            print("Initializing bluetooth failed: " + str(ex))

    def shutdownBluetooth(self):
        print("Shutdown Blueooth socket")
        self._socket.shutdown(2)

    def _updateContextLoop(self):
        """Starts an indefinitive loop to receive messages from the Bluetooth socket."""

        msg = ""
        while not self.stop:
            try:
                msg += self._socket.recv(1024)
            except BaseException as e:
                print("Error receiving bluetooth data: " + str(e))
                print("Attempting to reconnect...")
                self._tryConnect()
                continue

            # New line characaters is the end of the message
            msgEnd = msg.find('\n')

            if msgEnd == -1:
                # We have not received a complete message yet,
                # keep reading until we find a \n
                continue

            # Read all data until end of message index
            data = msg[:msgEnd]

            try:
                # Read joystick position
                xs = data.split(',')

                if len(xs) != 7:
                    print("Wrong message, expected 7 arguments. Goto next message.")
                    msg = msg[msgEnd + 1:]
                    continue

                self.context.jX = float((float(xs[0]) - 512.0) / 512.0)
                self.context.jY = float((float(xs[1]) - 512.0) / 512.0)
                self.context.jZ = float(xs[2])

                axStr = xs[3]
                ayStr = xs[4]

                # Only read AX/AY when it's sent with Bluetooth
                if axStr != "" and ayStr != "":
                    self.context.aX = float(axStr)
                    self.context.aY = -float(ayStr) #Note: the y angle is inversed here
            except:
                # Skip error and continue with next message
                msg = msg[msgEnd + 1:]
                continue

            self.context.jAngle = math.atan2(self.context.jY, self.context.jX) * (180 / math.pi) + 180
            magnitude = math.sqrt((self.context.jX ** 2) + (self.context.jY ** 2))
            self.context.jMagnitude = min(magnitude, 1)

            # Read the mode and action
            mode = xs[5]
            action = xs[6]

            mode = mode.lower().strip()
            action = action.lower().strip()

            resetBehavior = False
            if mode != self._oldMode or action != self._oldAction:
                if mode == "":
                    if action == "":
                        print("Reset spider status")
                        resetBehavior = True

                    elif action == "shutdown":
                        print("Goodbye.")
                        self._spider.shutdown()
                        break

                    elif action == "reboot":
                        print("Back in a sec.")
                        self._spider.reboot()
                        break

                elif mode == "limbo":
                    wideWalk = action == "stop"
                    print ("Enable wide walk: " + str(wideWalk))
                    self._spider.animationController.setWideWalking(wideWalk)

                elif mode == "sprint":
                    if action == "start":
                        print ("Start sprint mode")
                        self._spider.switchBehavior(BehaviorType.Sprint)
                    else:
                        print("Stop sprint mode")
                        resetBehavior = True

                elif mode == "gravel":
                    highWalk = action == "start"
                    print ("Set gravel mode: " + str(highWalk))
                    self._spider.animationController.setHighWalking(highWalk)

                elif mode == "spider-gap":
                    if action == "walk":
                        resetBehavior = True

                    elif action == "horizontal":
                        print ("Keeping body horizontal")
                        self._spider.switchBehavior(BehaviorType.ManualHorizontal)

                    elif action == "cross":
                        print ("Cross spider gap")
                        self._spider.switchBehavior(BehaviorType.Push)

                    elif action == "touch":
                        print ("Glas aanficken")
                        self._spider.switchBehavior(BehaviorType.Touch)

                elif mode == "vision":
                    if action == "start":
                        print("Start autonome destroy balloon")
                        self._spider.switchBehavior(BehaviorType.AutonomeDestroyBalloon)
                    elif action == "follow":
                        print("Start autonome follow balloon")
                        self._spider.switchBehavior(BehaviorType.AutonomeFollowBalloon)
                    else:
                        print("Stop vision behavior")
                        resetBehavior = True

                elif mode == "fury-road":
                    if action == "start":
                        print ("Start fury road")
                        self._spider.switchBehavior(BehaviorType.AutonomeFuryRoad)
                    else:
                        print("Stop fury road")
                        resetBehavior = True

                elif mode == "mating":
                    resetBehavior = True

                    if action == "pre-stab":
                        print ("Pre stab mating")
                        self._spider.sequenceController.parseSequence('../sequences/pre-stab-mating.txt')
                    elif action == "post-stab":
                        print ("Post stab mating")
                        self._spider.sequenceController.parseSequence('../sequences/post-stab-mating.txt')
                    elif action == "up":
                        print ("Moving spider up")
                        self.context.zOffset = 3
                        self._spider.switchBehavior(BehaviorType.Manual)
                        self._spider.animationController.setWideWalking(True)
                        self._spider.animationController.setHighWalking(False)
                        resetBehavior = False
                    elif action == "stab":
                        print ("Stab mating")
                        self._spider.sequenceController.parseSequence('../sequences/stab-mating.txt')

                if resetBehavior:
                    self._spider.switchBehavior(BehaviorType.Manual)
                    self._spider.animationController.setWideWalking(True)
                    self._spider.animationController.setHighWalking(False)
                    self.context.zOffset = 0

                # Save current action and messages
                self._oldMode = mode
                self._oldAction = action

            # Continue with next message
            msg = msg[msgEnd + 1:]

        self.shutdownBluetooth()
