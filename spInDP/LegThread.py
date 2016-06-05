import time
import threading


class LegThread(threading.Thread):
    """Provides a thread for handling leg movements."""

    cCoordinates = [0,0,0]

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
                legMovement = q.get()
                                
                if (legMovement.empty is False):
                    self.sequenceController.servoController.move(
                        (self.legId - 1) * 3 + 1, legMovement.coxa, legMovement.coxaSpeed)
                    self.sequenceController.servoController.move(
                        (self.legId - 1) * 3 + 2, legMovement.femur, legMovement.femurSpeed)
                    self.sequenceController.servoController.move(
                        (self.legId - 1) * 3 + 3, legMovement.tibia, legMovement.tibiaSpeed)

                #Sleep this thread for maxexectime seconds (until the move has been completed)
                time.sleep(legMovement.maxExecTime if legMovement.maxExecTime > 0 else 0.005)
                self.cCoordinates = legMovement.IKCoordinates
            #except:
                #print ("error on leg " + str(self.legId))
            finally:
                # Mark the task as done in the queue.
                q.task_done()
              
        print ("while loop quited")
        return
