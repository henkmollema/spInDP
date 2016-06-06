from spInDP.AutonomeBehavior import AutonomeBehavior
from spInDP.SequenceFrame import SequenceFrame
import time
import math

class ImmediateBehavior(AutonomeBehavior):
    """Provides autonome behavior for destroying a red balloon."""
    
    #An array of IKCoordinates
    basePose = [[-7,-8,5],[-7,-8,5],[-5,0,5],[-7,8,5],[-7,8,5],[-5,0,5]]
    currentPose = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    remoteContext = None
    
    #Physical dimensions
    bodytoSensorMid = 0  # from mid body to mid coxas X
    bodytoSensor = 12.05 # from mid body to back and front coxas X
    bodyToSide = 10.45 + 16.347 #from mid body to side leg coxa Y
    
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
        yAngle = 0
        xAngle = 0
        if(self.remoteContext.jMagnitude > 0.1):
                yAngle = self.remoteContext.jX * 15 * math.pi / 180
                xAngle = self.remoteContext.jY * 15 * math.pi / 180

        
        for x in range(1,7):
            newIKCoordinates = list(self.basePose[x - 1]) #copy the basePose

            #Change the z-coordinate based on joystick position and legID
            if (x == 1 or x == 2 ): #front legs
                newIKCoordinates[2] += math.sin(yAngle) * (self.bodytoSensor - self.basePose[x - 1][1]) / 2
                if x == 1:
                    newIKCoordinates[2] -= math.sin(xAngle) * (self.bodyToSide + self.basePose[x - 1][0]) / 2
                if x == 2:
                    newIKCoordinates[2] += math.sin(xAngle) * (self.bodyToSide + self.basePose[x - 1][0]) / 2
            elif (x == 4 or x == 5): #back legs
                newIKCoordinates[2] += math.sin(yAngle) * -(self.bodytoSensor + self.basePose[x - 1][1]) / 2
                if x == 5:
                    newIKCoordinates[2] += math.sin(xAngle) * -(self.bodyToSide + self.basePose[x - 1][0]) / 2
                if x == 4:
                    newIKCoordinates[2] += math.sin(xAngle) * (self.bodyToSide + self.basePose[x - 1][0]) / 2
            else: #side legs
                newIKCoordinates[2] += math.sin(yAngle) * (self.basePose[x - 1][1]) / 2
                if x == 6:
                    newIKCoordinates[2] += math.sin(xAngle) * -(self.bodyToSide + self.basePose[x - 1][0]) / 2
                if x == 3:
                    newIKCoordinates[2] += math.sin(xAngle) * (self.bodyToSide + self.basePose[x - 1][0]) / 2
            
            self.currentPose[x - 1] = newIKCoordinates
    
        #Set the servos to the currentpose with speed 150
        newFrame = self.poseToSequenceFrame(self.currentPose, 200)
        self.spider.sequenceController.setFrame(newFrame)
        
    def poseToSequenceFrame(self, pose, speed):
        seqFrame = SequenceFrame()
        for x in range(0,6):
            seqFrame.movements[x + 1] = self.spider.sequenceController.coordsToLegMovement(pose[x][0], pose[x][1], pose[x][2], x + 1, speed, immediateMode = True)
        
        return seqFrame
        
            
           