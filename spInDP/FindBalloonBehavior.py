from spInDP.AutonomeBehavior import AutonomeBehavior
import time
import math

class FindBalloonBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon"""

    centerDeviation = 100
    blobSizeArrive = 200
    frameNr = 0

    def __init__(self, spider):
        super(FindBalloonBehavior, self).__init__(spider)

    deltaTime = 0
    startTime = 0
    stabPosition = False
    def update(self):
        balloonFound, coords, size = self.spider.visioncontroller.FindBalloon()

        if(balloonFound):
            if(size >= self.blobSizeArrive):
                # When the balloon blob is big enough
                print("!!! Steek 'm in z'n rug !!!")
                
                if (not self.stabPosition):
                    self.spider.sequenceController.executePreStabLeft()
                    self.stabPosition = True
                
                print("execute stab")
                self.spider.sequenceController.executeStabLeft()
            else:
                x = coords[0]
                y = coords[1]
                a = 240
                b = x
                
                # Angle to balloon in degrees
                angle = math.atan(b / a) * (180 / math.pi)
                angle *= 1.5
                
                #print ("Walking with angle: " + str(angle) + " a: " + str(a) + " b: " + str(b))
                
                # Walk towards balloon
                execTime = self.spider.animationController.walk(angle, speedMod=1.5, frameNr=self.frameNr)
                time.sleep(execTime)
                #print "Exectime: " + str(execTime);
                self.stabPosition = False
                self.frameNr += 1
        
        ctime = time.time()
        deltaTime = ctime - self.startTime
        self.startTime = ctime
 