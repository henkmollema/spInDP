import time

from spInDP.Behavior import Behavior


class ManualBehavior(Behavior):
    """Provides manual behavior of a spider using the RemoteContext."""
    frameNr = 0
    turnMode = False
    lastZ = 0

    def __init__(self, spider):
        """Initializes a new instance of the ManualBehavior class."""

        super(ManualBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.context

        # self.spider.sensorDataProvider.startMeasuring()

    def update(self):
        jX = self.remoteContext.jX
        jY = self.remoteContext.jY
        jZ = self.remoteContext.jZ
        jAngle = self.remoteContext.jAngle
        jMagnitude = self.remoteContext.jMagnitude

        if self.lastZ != jZ:
            self.lastZ = jZ
            if jZ == 1:
                self.turnMode = not self.turnMode
                print ("Switch turnmode " + str(self.turnMode))

        # print "Joystick = X: " + str(jX) + ", Y: " + str(jY) + ", Z: " + str(jZ) + " magnitude: " + str(magnitute) + " angle: " + str(angle)

        # DEBUG
        # print "GYRO Y: " + str(((float(self.spider.sensorDataProvider.getAccelerometer()[1]) / 1000.0) / 16.0) * 90.0)
        # time.sleep(self.spider.animationController.walk(direction = 0, frameNr = 0, speedMod = 1, keepLeveled = True))
        # self.frameNr += 1
        # print "GYRO ANGLES: " + str(self.spider.sensorDataProvider.getAccelerometer()[0]) + ", " + str(self.spider.sensorDataProvider.getAccelerometer()[1]) + ", " + str(self.spider.sensorDataProvider.getAccelerometer()[2])
        # DEBUG


        if (jMagnitude > 0.4):
            speedModifier = jMagnitude * 2

            if not self.turnMode:  # strafemode
                time.sleep(max(self.spider.animationController.walk(
                    direction=jAngle, frameNr=self.frameNr,
                    speedMod=speedModifier) - self.spider.UPDATE_SLEEP_TIME,
                               0))
            else:
                if jAngle > 0:
                    turnAngle = 1
                else:
                    turnAngle = -1

                time.sleep(max(self.spider.animationController.turn(
                    direction=turnAngle, frameNr=self.frameNr,
                    speedMod=speedModifier) - self.spider.UPDATE_SLEEP_TIME,
                               0))

            self.frameNr += 1
        return

    def restrict(self, val, minval, maxval):
        if val < minval:
            return minval
        elif val > maxval:
            return maxval

        return val
