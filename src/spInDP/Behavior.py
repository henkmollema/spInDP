import abc

class Behavior(object):
    """Behavior base class."""

    def __init__(self):
      __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self):
      """Update of the behavior"""
      return
