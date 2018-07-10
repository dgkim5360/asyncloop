import collections


class ConfinedMap(collections.UserDict):
    """List with size limit to contain and control running jobs.

    >>> instance = ConfinedMap(maxsize=3)
    >>> bool(instance)
    False
    >>> len(instance)
    0
    >>> instance.maxsize
    3
    >>> instance.is_full()
    False
    >>> instance[1] = 10; instance[2] = 20; instance[3] = 30
    >>> len(instance)
    3
    >>> instance.is_full()
    True
    >>> instance[4] = 40
    Traceback (most recent call last):
        ...
    RuntimeError: This map is currently full.
    >>> val = instance.pop(1)
    >>> val
    10
    >>> len(instance)
    2
    >>> for k, v in instance.items():
    ...     print(k, v)
    2 20
    3 30
    """
    def __init__(self, maxsize=100):
        super().__init__()
        self._maxsize = maxsize

    def __setitem__(self, key, value):
        if len(self) == self._maxsize:
            raise RuntimeError('This map is currently full.')
        super().__setitem__(key, value)

    def qsize(self):
        return len(self)

    @property
    def maxsize(self):
        return self._maxsize

    def is_full(self):
        return len(self) >= self._maxsize
