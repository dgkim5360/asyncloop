class ConfinedSet:
    """List with size limit to contain and control running jobs"""
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

    def qsize(self):
        return len(self)

    @property
    def maxsize(self):
        return self._maxsize

    def add(self, item):
        if self.qsize() == self._maxsize:
            raise RuntimeError('The list is currently full')
        self._data.add(item)

    def remove(self, item):
        self._data.remove(item)

    def discard(self, item):
        self._data.discard(item)

    def pop(self):
        return self._data.pop()

    def is_full(self):
        return self.qsize() >= self._maxsize
