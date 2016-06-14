import time
from spInDP.Behavior import Behavior


class TouchBehavior(Behavior):
    frameNr = 0
    animationController = None
    sensorData = None
    spiderAngle = 0
    yRotation = 0

    def __init__(self, spider):
        print("Initializing touch behavior.")
        super(TouchBehavior, self).__init__(spider)
        self.measureSpinAngle()
        self.initLeg()

    def update(self):
        jMagnitude = self.spider.remoteController.context.jMagnitude
        x = self.spider.remoteController.context.jX

        if (jMagnitude > 0.4):
            # time.sleep(max(self.animationController.method))
            print(jMagnitude)
            self.frameNr += 1
            currentAngle = self.spider.sequenceController.servoController.getPosition(servo=1)
            if x > 0:
                print("if")
                self.spider.sequenceController.servoController.move(servo=1, angle=currentAngle - 1, speed=50*jMagnitude)
            else:
                print("else")
                self.spider.sequenceController.servoController.move(servo=1, angle=currentAngle + 1, speed=50*jMagnitude)

        return

    def initLeg(self):
        print("Init leg.")
        # femur
        self.spider.sequenceController.servoController.move(servo=2, angle=-30, speed=100)
        time.sleep(0.8)
        # coxa
        self.spider.sequenceController.servoController.move(servo=1, angle=-45, speed=100)
        time.sleep(0.8)
        # tibia
        self.spider.sequenceController.servoController.move(servo=3, angle=0, speed=100)
        time.sleep(0.8)
        # femur
        self.spider.sequenceController.servoController.move(servo=2, angle=-90 + self.yRotation, speed=100)
        time.sleep(0.8)

    def measureSpinAngle(self):
        sensorData = self.spider.sensorDataProvider
        sensorData.startMeasuring()
        time.sleep(0.1)
        sensorData.stopMeasuring()
        #x, y, z = sensorData.getAccelerometer()
        x = sensorData.getAccelerometer()
        #self.yRotation = sensorData.getYRotation(x, y, z)
        #self.yRotation = x * 180
        self.yRotation = 12
        print("y: ", x, " yRottion: ", self.yRotation)