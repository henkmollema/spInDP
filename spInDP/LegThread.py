import time
import threading


class LegThread(threading.Thread):
    """Provides a thread for handling leg movements."""

    def __init__(self, legId, sequenceController, group=None, target=None, args=(), kwargs=None, verbose=None):
        super(LegThread, self).__init__()
        self.target = target
        self.name = 'LegThread' + str(legId)
        self.deamon = True
        self.legId = legId
        self.sequenceController = sequenceController
        return

    def run(self):
        q = self.sequenceController.legQueue[self.legId]
        while not self.sequenceController.stopped:
            try:
                vLeg = q.get()
                                
                if (vLeg.empty is False):
                    self.sequenceController.servoController.move(
                        (self.legId - 1) * 3 + 1, vLeg.coxa, vLeg.coxaSpeed)
                    self.sequenceController.servoController.move(
                        (self.legId - 1) * 3 + 2, vLeg.femur, vLeg.femurSpeed)
                    self.sequenceController.servoController.move(
                        (self.legId - 1) * 3 + 3, vLeg.tibia, vLeg.tibiaSpeed)
                
                time.sleep(vLeg.maxExecTime if vLeg.maxExecTime > 0 else 0.005)
            #except:
                #print ("error on leg " + str(self.legId))
            finally:
                # Mark the task as done in the queue.
                q.task_done()
              
        print ("while loop quited")
        return
