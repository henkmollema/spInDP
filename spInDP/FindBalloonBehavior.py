from spInDP.AutonomeBehavior import AutonomeBehavior
import time

class FindBalloonBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon"""
    
    centerDeviation = 24
    blobSizeArrive = 200
    
    def __init__(self, spider):
        super(FindBalloonBehavior, self).__init__(spider)

    def update(self):
        print("Update from AutonomeBehavior")
        balloonFound, coords, size  = self.spider.visioncontroller.FindBalloon()
        
        if(balloonFound):
            if(abs(coords[0]) > self.centerDeviation):
                #Adjust horizontal
                if(coords[0] > 0):
                    time.sleep(self.spider.sequencecontroller.executeStepRight() + 0.5)
                    return
                else:
                    time.sleep(self.spider.sequencecontroller.executeStepLeft() + 0.5)
                    return

                return
            else:
                #When the balloon is center screen
                if(size >= self.blobSizeArrive):
                    #When the balloon blob is big enough
                    #Steek m in z'n rug
                    time.sleep(1)
                else:
                    #If the balloon blob is not big enough, take a step forward
                    time.sleep(self.spider.sequencecontroller.executeStepForward() + 0.5)
                    return 
            
            
            
        time.sleep(1000);
