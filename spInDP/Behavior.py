import abc


class Behavior(object):
    """Base class of behavior of a spider."""

    def __init__(self):
        __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self):
        """Update of the behavior"""
        return
