import abc


class Behavior(object):
    """Base class of behavior of a spider."""
    spider = None

    def __init__(self, spider):
        """Initializes a new instance of the Behavior class."""

        __metaclass__ = abc.ABCMeta
        self.spider = spider

    @abc.abstractmethod
    def update(self):
        """Update of the behavior"""
        return
