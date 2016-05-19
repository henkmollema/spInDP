from spInDP.LegMovement import LegMovement

class SequenceFrame(object):
  movements = { }
  
  def getScaledMovements(self):
    times = []
    for k in self.movements:
      times.append(self.movements[k].maxExecTime)
      
    maxMaxExec = max(times)
  
    for k in self.movements:
      mov = self.movements[k]
      scaleFactor = mov.maxExecTime / maxMaxExec
      
      newMov = LegMovement()
      newMov.coxa = mov.coxa
      newMov.tibia = mov.tibia
      newMov.femur = mov.femur
      
      newMov.coxaSpeed = mov.coxaSpeed * scaleFactor
      newMov.tibiaSpeed = mov.tibiaSpeed * scaleFactor
      newMov.femurSpeed = mov.femurSpeed * scaleFactor
      
      newMov.maxExecTime = mov.maxExecTime * scaleFactor
      
      yield (k, newMov)
