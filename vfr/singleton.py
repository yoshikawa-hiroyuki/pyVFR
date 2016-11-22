"""
This is an implementation of Singleton pattern in python.
see http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/412551
"""

class Singleton(type):
    """This is an implementation of the singleton
    without using the __new__ class
    but by implementing the __call__ method in the metaclass.
    """
    def __init__(self, *args):
        type.__init__(self, *args)
        self._instances = {}

    def __call__(self, *args):
        if not args in self._instances:
            self._instances[args] = type.__call__(self, *args)
        return self._instances[args]
