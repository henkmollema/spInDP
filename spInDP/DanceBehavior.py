from spInDP.Behavior import Behavior
import time

class DanceBehavior(Behavior):
    startTime = 0
    moveNR = 1
    frameNr = 0

    def __init__(self,spider):
        super(DanceBehavior,self).__init__(spider)
        #self.dance()
        self.startTime = time.time()

    def update(self):
        t = time.time() - self.startTime

        #start dance
        #first move
        if(t < 3 and self.moveNR == 1):
            print self.moveNR
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-move-1.txt",speedModifier=1.3))
            self.moveNR += 1
        if(t > 3 and t < 4.5  and self.moveNR == 2):
            print self.moveNR
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-move-2.txt",speedModifier=1.3))
            self.moveNR += 1
            return

        if (t > 4.5 and t < 6.3 and self.moveNR == 3):
            print self.moveNR
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-move-3-6.txt",speedModifier=1.3))
            self.moveNR += 1
            return

        if (t > 6.3 and t < 10 and self.moveNR == 4):
            print self.moveNR
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-move-4-plie.txt",speedModifier=1.3))
            self.moveNR += 1
            return

        if (t > 10 and t < 12.77 and self.moveNR == 5):
            print self.moveNR
            #time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-move-5.txt",speedModifier=1.3))
            self.moveNR += 1
            return

        if (t > 12.77 and t < 15.8 and self.moveNR == 6):
            print self.moveNR
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-move-3-6.txt",speedModifier=1.3))
            self.moveNR += 1
            return

        if (t > 15.8 and t < 19.23 and self.moveNR == 7):
            print self.moveNR
            self.pirouette()
            self.moveNR += 1
            return

        # if (t > 19.23 and t < 20.7):
        if (t > 19.23 and t < 22):
            time.sleep(self.spider.animationController.strafeWalk(frameNr=self.frameNr, direction=90))
            self.moveNR = 10
            return

        # if (t > 20.7 and t < 22):
        #     print self.moveNR
        #     time.sleep(self.spider.animationController.strafeWalk(frameNr=self.frameNr, direction=-90))
        #
        #     self.moveNR = 10
        #     return

        if (t > 22 and t < 26 and self.moveNR == 10):
            print self.moveNR
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-move-3-6.txt",speedModifier=1.3))
            self.moveNR += 1
            return

        #EVEN NIET BEWEGEN HIER

        if (t > 28 and t < 29.3 and self.moveNR == 11):
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-wave.txt"))
            self.moveNR += 1
            return

        if (t > 29.3 and t < 32.3 and self.moveNR == 12):
            # Empty move for now
            self.moveNR += 1
            return
        if (t > 32.3 and t < 35.63 and self.moveNR == 13):
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-circle-air.txt"))
            self.moveNR += 1
            return
        if (t > 35.63 and t < 38.54 and self.moveNR == 14):
            time.sleep(self.spider.animationController.strafeWalk(direction=0,frameNr=self.frameNr))
            self.frameNr += 1
            self.moveNR += 1
            return

        if (t > 38.54 and t < 40 and self.moveNR == 15):
            time.sleep(self.spider.animationController.strafeWalk(direction=180, frameNr=self.frameNr))
            self.frameNr += 1
            self.moveNR += 1
            return

        if (t > 40 and t < 45 and self.moveNR == 16):
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-stretchwave-5seconds.txt"))
            self.moveNR += 1
            return

        if (t > 45 and t < 47 and self.moveNR == 17):
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-side-to-side-2sec.txt"))
            self.moveNR += 1
            return

        if (t > 47 and t < 51):
            time.sleep(self.spider.animationController.strafeWalk(frameNr=self.frameNr, direction=-90))

            self.moveNR = 19
            return

        if (t > 51 and t < 54 and self.moveNR == 19):
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-go-high.txt"))
            self.moveNR += 1
            return

        if (t > 54 and t < 56 and self.moveNR == 20):
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-go-higher.txt"))
            self.moveNR += 1
            return

        if (t > 56 and t < 57 and self.moveNR == 21):
            time.sleep(self.spider.sequenceController.parseSequence("sequences/dance-go-low.txt"))
            self.moveNR += 1
            return

        #at 57 we need to be low here

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
        startTime = time.time()
        print("start music")

    def execSequence(self, animation, repeat, speedModifier):
        return self.spider.sequenceController.parseSequence("sequences/"+ animation, repeat=int(repeat), speedModifier=float(speedModifier))

    def graceStrafe(self):
        totalTime = 0
        frameNr = 0
        execTime = 0
        for x in range(1, 28):
            execTime = self.spider.animationController.strafeWalk(direction=60 + x * 5, frameNr=frameNr, speedMod=1.5, keepLeveled=True)
            totalTime += execTime
            time.sleep(execTime)
            frameNr += 1
        frameNr = 0
        for x in range(1, 28):
            execTime = self.spider.animationController.strafeWalk(direction=240 - x * 5, frameNr=frameNr, speedMod=1.5, keepLeveled=True)
            totalTime += execTime
            time.sleep(execTime)
            frameNr += 1

        return totalTime

    def pirouette(self, xDirection = 1, speedMod = 5, stepSize = 4, keeplevel = False):
        return self.turn(repeat=8, xDirection=xDirection, speedMod=speedMod, stepSize=stepSize, keepLevel=keeplevel)

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