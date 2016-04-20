import threading, time
from threading import Thread
from RemoteController import RemoteController
from ManualBehavior import ManualBehavior
from AutonomeBehavior import AutonomeBehavior
from BehaviorType import BehaviorType

class Spider(object):
    """Encapsulates the interaction with the spider."""
    
    stopLoop = False

    def __init__(self):
        self.remoteController = RemoteController(self)

    def updateLoop(self):
        while (self.stopLoop == False):
            #print("update loop " + str(self))
            self.behavior.update()
            time.sleep(0.0166667)
            
    def startUpdateLoopThread(self):
        self.thread = Thread(target = self.updateLoop)
        self.thread.start() 

    def initBevahiorLoop(self):    
        print("initBevahiorLoop")
        self.behavior = ManualBehavior()
        self.startUpdateLoopThread()

    def switchBehavior(self, behaviorType):
        print("switchBehavior invoked")
        
        # Stop the update loop
        self.stopLoop = True
        self.thread.join()
        print("Update loop stopped")
                
        # Switch to the desired behavior
        if (behaviorType == BehaviorType.Manual):
            print("Switched to manual behavior")
            self.behavior = ManualBehavior()
        elif (behaviorType == BehaviorType.Autonome):
            print("Autonome behavior not implemented")
            self.behavior = AutonomeBehavior()
            
        # Start the loop again
        self.stopLoop = False
        self.startUpdateLoopThread()
        
    def stop(self):
        self.stopLoop = True
        self.thread.join()
        print("Stopped the spider")
