class PendingJob:
    """A container to store a coroutine and its callback,
    to be stored in the pending queue."""
    def __init__(self, job_coro, callback=None):
        self.job_coro = job_coro
        self.callback = callback
