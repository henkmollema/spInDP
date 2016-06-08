from spInDP.Behavior import Behavior
import time
from spInDP.AnimationController import AnimationController
from spInDP.SensorDataProvider import SensorDataProvider

class TouchBehavior(Behavior):
    frameNr = 0
    animationController = None
    sensorData = None

    def __init__(self, spider):
        print("Initializing touch behavior.")
        super(TouchBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.context
        self.animationController = AnimationController(spider)
        self.sensorData = SensorDataProvider()
        self.initLeg()

    def update(self):
        jMagnitude = self.remoteContext.jMagnitude

        if(jMagnitude > 0.4):
            #time.sleep(max(self.animationController.method))
            self.frameNr += 1

        return

    def initLeg(self):
        angle = self.sensorData.startMeasuring()
