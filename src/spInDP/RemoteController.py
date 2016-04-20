class RemoteController(object):
    """Provides interaction with the physical remote controller."""

    def __init__(self, spider):
        self.spider = spider

    def printInfo(self):
        print("spider is None: " + str(self.spider is None))
