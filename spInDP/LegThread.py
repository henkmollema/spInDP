import time
import threading


class LegThread(threading.Thread):
    """Provides a thread for handling leg movements."""

    _cCoordinates = [0, 0, 0]

    def __init__(self, legId, sequenceController, group=None, target=None, args=(), kwargs=None, verbose=None):
        """Initializes a new instance of the LegThread class."""

        super(LegThread, self).__init__()
        self.target = target
        self.name = 'LegThread' + str(legId)
        self.deamon = True

        self._legId = legId
        self._sequenceController = sequenceController

    def run(self):
        queue = self._sequenceController.legQueue[self._legId]
        while not self._sequenceController.stopped:
            try:
                legMovement = queue.get()

                if (legMovement.empty is False):
                    self._sequenceController.servoController.move(
                        (self._legId - 1) * 3 + 1, legMovement.coxa, legMovement.coxaSpeed)
                    self._sequenceController.servoController.move(
                        (self._legId - 1) * 3 + 2, legMovement.femur, legMovement.femurSpeed)
                    self._sequenceController.servoController.move(
                        (self._legId - 1) * 3 + 3, legMovement.tibia, legMovement.tibiaSpeed)

                # Sleep this thread for maxexectime seconds (until the move has been completed)
                time.sleep(legMovement.maxExecTime if legMovement.maxExecTime > 0 else 0.005)
                self._cCoordinates = legMovement.IKCoordinates
                # except:
                # print ("error on leg " + str(self.legId))
            finally:
                # Mark the task as done in the queue.
                queue.task_done()

        print ("While loop of " + self.name + " stopped.")
