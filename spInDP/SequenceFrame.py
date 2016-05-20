from spInDP.LegMovement import LegMovement

class SequenceFrame(object):
  movements = { }
  maxMaxExecTime = 0.0
  
  def getScaledMovements(self):
    times = []
    for k in self.movements:
      times.append(self.movements[k].maxExecTime)
      
    self.maxMaxExecTime = max(times)
    scaledMoves = { }
    for k in self.movements:
      mov = self.movements[k]
      scaleFactor = mov.maxExecTime / self.maxMaxExecTime
      
      newMov = LegMovement()
      newMov.coxa = mov.coxa
      newMov.tibia = mov.tibia
      newMov.femur = mov.femur
      
      newMov.coxaSpeed = mov.coxaSpeed * scaleFactor
      newMov.tibiaSpeed = mov.tibiaSpeed * scaleFactor
      newMov.femurSpeed = mov.femurSpeed * scaleFactor
      
      newMov.maxExecTime = mov.maxExecTime * scaleFactor
      
      scaledMoves[k] = newMov
    return scaledMoves