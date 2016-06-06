from spInDP.AutonomeBehavior import AutonomeBehavior
from spInDP.SequenceFrame import SequenceFrame
import time
import math

class ImmediateBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon."""
    
    #An array of IKCoordinates
    basePose = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    currentPose = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    remoteContext = None
    
    #Physical dimensions
    bodytoSensorMid = 0  # from mid body to mid coxas X
    bodytoSensor = 12.05 # from mid body to back and front coxas X
    bodyToSide = 9.11 #from mid body to side leg coxa Y
    
    def __init__(self, spider):
        super(ImmediateBehavior, self).__init__(spider)
        self.remoteContext = self.spider.remoteController.context
        
    def update(self):
        """
        Manipulate the currentpose based on input or sensors
        Please note only the z coordinate can be safely modified
        when manipulating the x or y coordinate make sure the leg
        is in the air.
        """
        for x in range(1,7):
            newIKCoordinates = self.basePose[x]
            
            if(self.remoteContext.jMagnitude > 0.1):
                yAngle = self.remoteContext.jY * 10 
                xAngle = self.remoteContext.jX * 10 
            else:
                yAngle = 0
                xAngle = 0
            
            #Change the z-coordinate based on joystick position and legID
            if (x == 1 or x == 2 ): #front legs
                newIKCoordinates[2] += math.sin(yAngle) * (self.bodytoSensor - self.basePose[x][1])
                if x == 1:
                    newIKCoordinates[2] -= math.sin(xAngle) * (self.bodyToSide + self.basePose[x][0])
                if x == 2:
                    newIKCoordinates[2] += math.sin(xAngle) * (self.bodyToSide + self.basePose[x][0])
            elif (x == 4 or x == 5): #back legs
                newIKCoordinates[2] += math.sin(yAngle) * -(self.bodytoSensor + self.basePose[x][1])
                if x == 5:
                    newIKCoordinates[2] -= math.sin(xAngle) * (self.bodyToSide + self.basePose[x][0])
                if x == 4:
                    newIKCoordinates[2] += math.sin(xAngle) * (self.bodyToSide + self.basePose[x][0])
            else: #side legs
                newIKCoordinates[2] += math.sin(yAngle) * (self.basePose[x][1])
                if x == 5:
                    newIKCoordinates[2] -= math.sin(xAngle) * (self.bodyToSide + self.basePose[x][0])
                if x == 4:
                    newIKCoordinates[2] += math.sin(xAngle) * (self.bodyToSide + self.basePose[x][0])
            
            self.currentPose[x] = newIKCoordinates
    
        #Set the servos to the currentpose with speed 50
        newFrame = self.poseToSequenceFrame(self.currentPose, 50)
        self.spider.sequenceController.setFrame(newFrame)
        
    def poseToSequenceFrame(self, pose, speed):
        seqFrame = SequenceFrame()
        for x in range(1,7):
            seqFrame.movements[x] = self.spider.sequenceController.coordsToLegMovement(pose[x][0], pose[x][1], pose[x][2], speed)
        
        return seqFrame
        
            
           