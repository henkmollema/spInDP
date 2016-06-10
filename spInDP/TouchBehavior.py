class TouchBehavior(Behavior):

    frameNr = 0
    animationController = None
    sensorData = None
    spiderAngle = 0
    yRotation = 0
    spider = None

    def __init__(self, spider):
        print("Initializing touch behavior.")
        super(TouchBehavior, self).__init__(spider)
        self.remoteContext = spider.remoteController.context
        self.animationController = AnimationController(spider)
        self.sensorData = SensorDataProvider()
        self.spider = spider
        self.initLeg()

    def update(self):
        jMagnitude = self.remoteContext.jMagnitude

        if(jMagnitude > 0.4):
            #time.sleep(max(self.animationController.method))
            self.frameNr += 1

        return

    def initLeg(self):
        # femur
        self.spider.sequenceController.servoController.move(servo=2, angle=30, speed=100)
        #coxa
        self.spider.sequenceController.servoController.move(servo=1, angle=0, speed=100)
        #femur
        self.spider.sequenceController.servoController.move(servo=2, angle=90, speed=100)
        #tibia
        self.spider.sequenceController.servoController.move(servo=3, angle=0, speed=100)
        #coxa = 45 --> coxa = 90
        #femur = ~60 --> femur = 90 maar is afhankelijk van de hoek
        #tibia = ~60 --> tibia = 0

    def measureSpinAngle(self):
        sensorData = SensorDataProvider()
        sensorData.startMeasuring()
        time.sleep(0.1)
        sensorData.stopMeasuring()
        x, y, z = sensorData.getSmoothAccelerometer()
        print("x: ",  x, ", y: ", ", z: ", z)
        self.yRotation = sensorData.getYRotation(x, y, z)