from spInDP.LegMovement import LegMovement


class SequenceFrame(object):
    movements = {}
    maxMaxExecTime = 0.0

    def setMovement(self, legID, LegMovement):
        self.movements[legID] = LegMovement

    def getScaledMovements(self):
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
        return scaledMoves
