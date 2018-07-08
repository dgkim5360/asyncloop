class ConfinedSet:
    """List with size limit to contain and control running jobs.

    >>> instance = ConfinedSet(data=[1, 2, 3], maxsize=4)
    >>> bool(instance)
    True
    >>> len(instance)
    3
    >>> instance.qsize()
    3
    >>> instance.maxsize
    4
    >>> instance.is_full()
    False
    >>> instance.add(4)
    >>> instance.qsize()
    4
    >>> instance.remove(1)
    >>> instance.qsize()
    3
    >>> instance.pop()
    2
    >>> instance.qsize()
    2
    >>> instance.add(10)
    >>> instance.add(11)
    >>> instance.is_full()
    True
    >>> for item in instance:
    ...     print(item)
    3
    4
    10
    11
    """
    def __init__(self, data=None, maxsize=100):
        self._maxsize = maxsize
        if data is not None and len(data) > self._maxsize:
            raise ValueError('Inital data exceeds maxsize')
        if data is None:
            self._data = set()
        else:
            self._data = set(data)

    def __bool__(self):
        return bool(self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def qsize(self):
        return len(self)

    @property
    def maxsize(self):
        return self._maxsize

    def add(self, item):
        if self.qsize() == self._maxsize:
            raise RuntimeError('This set is currently full.')
        self._data.add(item)

    def remove(self, item):
        self._data.remove(item)

    def discard(self, item):
        self._data.discard(item)

    def pop(self):
        return self._data.pop()

    def is_full(self):
        return self.qsize() >= self._maxsize
