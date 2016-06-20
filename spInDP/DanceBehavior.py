from spInDP.Behavior import Behavior
import time

class DanceBehavior(Behavior):

    def __init__(self,spider):
        super(DanceBehavior,self).__init__(spider)
        self.dance()

    def update(self):
        self.spider.switchBehavior("Manual")

    def dance(self):
        print("I'm dancing!")
        # stretch
        print("stretch")
        time.sleep(self.execSequence("dance-stretch.txt", repeat=1, speedModifier=1))
        # start dance
        self.startMusic()
        print("graceStafe")
        time.sleep(self.graceStrafe())
        # spitzen
        print("spitzen")
        time.sleep(self.execSequence("dance-spitzen.txt", repeat=2, speedModifier=1))
        # plie
        print("plie")
        time.sleep(self.execSequence("dance-plie.txt", repeat=1, speedModifier=1))
        print("graceStafe")
        #time.sleep(self.graceStrafe())
        print("pirouette")
        time.sleep(self.pirouette())

    def startMusic(self):
        print("start music")

    def execSequence(self, animation, repeat, speedModifier):
        return self.spider.sequenceController.parseSequence("sequences/"+ animation, repeat=int(repeat), speedModifier=float(speedModifier))

    def graceStrafe(self):
        totalTime = 0
        frameNr = 0
        execTime = 0
        aX = 0
        for x in range(1, 28):
            aX = self.spider.remoteController.context.aX
            execTime = self.spider.animationController.strafeWalk(direction=60 + x * 5, frameNr=frameNr, speedMod=1.5, keepLeveled=True)
            totalTime += execTime
            time.sleep(execTime)
            frameNr += 1
        frameNr = 0
        for x in range(1, 28):
            execTime = self.spider.animationController.strafeWalk(direction=240 - x * 5, frameNr=frameNr, speedMod=1.5, keepLeveled=True, danceAngle=True, danceYAngle=angle)
            totalTime += execTime
            time.sleep(execTime)
            frameNr += 1

        return totalTime

    def pirouette(self,xDirection = 0, speedMod = 1, stepSize = 3.5, keeplevel = False):
        return self.turn(repeat=12, xDirection=xDirection, speedMod=speedMod, stepSize=stepSize, keepLevel=keeplevel)

    def turn(self, repeat = 0, xDirection = 0, speedMod = 1, stepSize = 3.5, keepLevel= False):
        frameNr = 0
        totalTime = 0
        execTime = 0
        for i in range(0,repeat):
            for x in range(0,6):
                execTime = self.spider.animationController.turnWalk(xDirection=xDirection,yDirection=0,frameNr=frameNr,speedMod=speedMod,stepSize=stepSize,keepLeveled=keepLevel)
                totalTime += execTime
                time.sleep(execTime)
                frameNr += 1

        return totalTime