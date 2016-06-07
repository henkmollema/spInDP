from spInDP.LegMovement import LegMovement


class SequenceFrame(object):
    """
        Holds one LegMovement objects for each leg
        The SequenceFrames are used to make sure
        all the legs start and stop moving at the same time.
    """

    movements = {}
    maxMaxExecTime = 0.0

    def setMovement(self, legID, LegMovement):
        """Set a LegMovement in this sequenceframe"""
        self.movements[legID] = LegMovement

    def getScaledMovements(self):
        """
            Scales the servo speeds in the LegMovements in this SequenceFrame
            so that all movements start and stop at the same time

            retuns a new list of scaled LegMovements
        """
        times = []
        for k in self.movements:
            if self.movements[k] is not None:
                times.append(self.movements[k].maxExecTime)

        if (len(times) == 0):
            self.maxMaxExecTime = 0
        else:
            self.maxMaxExecTime = max(times)

        scaledMoves = {}
        
        for k in self.movements:
            if self.movements[k] is not None:
                if(self.maxMaxExecTime != 0):
                    mov = self.movements[k]
                    scaleFactor = mov.maxExecTime / self.maxMaxExecTime

                    newMov = LegMovement()
                    newMov.coxa = mov.coxa
                    newMov.tibia = mov.tibia
                    newMov.femur = mov.femur

                    newMov.coxaSpeed = mov.coxaSpeed * scaleFactor
                    newMov.tibiaSpeed = mov.tibiaSpeed * scaleFactor
                    newMov.femurSpeed = mov.femurSpeed * scaleFactor

                    # newMov.maxExecTime = mov.maxExecTime * scaleFactor
                    newMov.maxExecTime = self.maxMaxExecTime

                    scaledMoves[k] = newMov
                else:
                    scaledMoves[k] = self.movements[k]
                    
        return scaledMoves
