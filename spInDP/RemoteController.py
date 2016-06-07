import bluetooth
import threading
import math
from spInDP.RemoteContext import RemoteContext


class RemoteController(object):
    """Provides interaction with the physical remote controller over Bluetooth."""

    stop = False
    context = None
    _spider = None
    _sock = None
    _updateLoop = None

    def __init__(self, spider):
        self._spider = spider
        self.context = RemoteContext()
        try:
            print("Initializing Bluetooth connection")
            self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self._sock.connect(("20:16:03:30:80:85", 1))
        except BaseException as e:
            print("Initializing bluetooth failed: " + str(e))

        self._updateLoop = threading.Thread(target=self.updateContextLoop)
        self._updateLoop.start()

    def updateContextLoop(self):
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
                 
            self.context.jAngle = math.atan2(self.context.jY, self.context.jX) * (180/math.pi) + 180
            magnitude = math.sqrt((self.context.jX**2) + (self.context.jY**2))
            self.context.jMagnitude = min(magnitude, 1)

            # Read the mode and action
            mode = xs[3]
            action = xs[4]

            mode = mode.lower()
            if mode == "limbo":
                print("limbo action: " + action)
                # Enable compact crab walk when 'start' is passed
                self._spider.animationController.setWideWalking(action == "start")

            elif mode == "sprint":
                if action == "start":
                    print ("Start sprint mode")
                else:
                    print("Stop sprint mode")

                print ("Sprint not implemented, using walk.")
                self._spider.animationController.setWideWalking(False)

            elif mode == "grind":
                if action == "start":
                    print ("Start grind mode")
                else:
                    print("Stop grind mode")

                print("Grind mode not enable, using walk.")
                self._spider.animationController.setWideWalking(False)

            elif mode == "spider-gap":
                if action == "walk":
                    print ("Regular walk")
                elif "action" == "body-horizontal":
                    print ("Keeping body horizontal")
                elif "gap":
                    print ("Cross spider gap")
                elif "touch-glass":
                    print ("Glas aanficken")

                print("Grind mode not enable, using walk.")
                self._spider.animationController.setWideWalking(False)

            elif mode == "destroy-balloon":
                if action == "start":
                    self._spider.switchBehavior("destoyballoon")
                else:
                    self._spider.switchBehavior("manual")

            elif mode == "fury-road":
                if action == "start":
                    print ("Start fury road")
                else:
                    print("Stop fury road")

                print("Grind mode not enable, using walk.")
                self._spider.animationController.setWideWalking(False)

            elif mode == "paringsdans":
                if action == "start":
                    print("Start paringsdans mode")
                elif action == "stop":
                    print ("Stop paringsdans mode")
                elif action == "up":
                    print ("Moving spider up")
                elif action == "down":
                    print ("Moving spider down")

            #Continue with next message
            msg = msg[msgEnd + 1:]

        print("Closing socket")
        self._sock.close()
