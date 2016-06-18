import time
from spInDP.Behavior import Behavior


class TouchBehavior(Behavior):
    frameNr = 0
    animationController = None
    currentAngleCoxa = 0
    currentAngleFemur = 0
    leftTouch = True
    servoIdCoxa = 0
    servoIdFemur = 0

    def __init__(self, spider):
        print("Initializing touch behavior.")
        super(TouchBehavior, self).__init__(spider)
        if self.leftTouch:
            time.sleep(self.spider.sequenceController.parseSequence('sequences/pre-touch-left.txt'))
            self.servoIdCoxa = 1
            self.servoIdFemur = 2
        else:
            time.sleep(self.spider.sequenceController.parseSequence('sequences/pre-touch-right.txt'))
            self.servoIdCoxa = 4
            self.servoIdFemur = 5
        self.currentAngleCoxa = self.spider.sequenceController.servoController.getPosition(servo=self.servoIdCoxa)
        self.currentAngleFemur = self.spider.sequenceController.servoController.getPosition(servo=self.servoIdFemur)
        print("coxa angle ", self.currentAngleCoxa)
        print("femur angle ", self.currentAngleFemur)

    def update(self):
        jMagnitude = self.spider.remoteController.context.jMagnitude
        xInput = self.spider.remoteController.context.jX
        yInput = self.spider.remoteController.context.jY

        if (jMagnitude > 0.4):
            print("manual touch")

            print("coxa angle ",self.currentAngleCoxa)
            print("femur angle ", self.currentAngleFemur)
            self.frameNr += 1
            x, y = self.cap(xInput, yInput)
            self.currentAngleCoxa += y
            self.currentAngleFemur += x
            self.spider.sequenceController.servoController.move(servo=self.servoIdCoxa, angle=self.currentAngleCoxa, speed=100 * jMagnitude)
            self.spider.sequenceController.servoController.move(servo=self.servoIdFemur, angle=self.currentAngleFemur, speed=100 * jMagnitude)
        return

    def cap(self, x, y):
        retX = 0
        retY = 0
        print("x: ", x, " y", y)
        if x > 0.5:
            retX = 0.1
        elif x < -0.5:
            retX = -0.1
        if y > 0.7:
            retY = 0.1
        elif y < -0.7:
            retY = -0.1
        print("retX, ", retX, " retY, ", retY)
        return retX, retY