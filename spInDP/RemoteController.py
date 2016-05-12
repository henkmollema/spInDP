from spInDP.RemoteContext import RemoteContext


class RemoteController(object):
    """Provides interaction with the physical remote controller."""

    Context = RemoteContext()

    def __init__(self, spider):
        self.spider = spider
