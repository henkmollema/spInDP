from spInDP.RemoteContext import RemoteContext
import glob
import json

RemoteControllerInstance = None

class RemoteController(object):
    """Provides interaction with the physical remote controller."""

    Context = RemoteContext()

    def __init__(self, spider):
        global RemoteControllerInstance
        self.spider = spider
        RemoteControllerInstance = self

 