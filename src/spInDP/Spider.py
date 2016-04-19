from RemoteController import RemoteController

class Spider(object):
    """Encapsulates the interaction with the spider."""

    def __init__(self):
        self.remoteController = RemoteController(self)

    def printHello(self):
        self.remoteController.printInfo()
        print("Hello world")