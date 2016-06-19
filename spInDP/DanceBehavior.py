from spInDP.Behavior import Behavior
import time

class DanceBehavior(Behavior):

    def __init__(self,spider):
        super(DanceBehavior,self).__init__(spider)
        self.dance()

    def update(self):
        print("dance")
        time.sleep(1)

    def dance(self):
        print("I'm dancing!")
        # stretch
        print("stretch")
        time.sleep(self.execSequence("dance-stretch.txt", repeat=1, speedModifier=1))
        # start dance
        self.startMusic()
        # spitzen
        print("spitzen")
        time.sleep(self.execSequence("dance-spitzen.txt", repeat=2, speedModifier=1))
        # plie
        print("plie")
        time.sleep(self.execSequence("dance-plie.txt", repeat=1, speedModifier=1))
        print("graceStafe")
        time.sleep(self.graceStrafe())

    def startMusic(self):
        print("start music")

    def execSequence(self, animation, repeat, speedModifier):
        return self.spider.sequenceController.parseSequence("sequences/"+ animation, repeat=int(repeat), speedModifier=float(speedModifier))

    def graceStrafe(self):
        totalTime = 0
        frameNr = 0
        execTime = 0
        for x in range(1, 28):
            execTime = self.spider.animationController.strafeWalk(direction=60 + x * 1, frameNr=frameNr, speedMod=1, keepLeveled=False, danceYAngle=0)
            totalTime += execTime
            print("execTime: ", execTime)
            time.sleep(execTime)
            frameNr += 1
        frameNr = 0
        for x in range(1, 28):
            execTime = self.spider.animationController.strafeWalk(direction=-240 - x * 1, frameNr=frameNr, speedMod=1, keepLeveled=False, danceYAngle=0)
            totalTime += execTime
            time.sleep(execTime)
            frameNr += 1

        return totalTime