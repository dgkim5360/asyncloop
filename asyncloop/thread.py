import asyncio
import threading
import queue

from asyncloop.set import ConfinedSet
from asyncloop.job import callback_done, AsyncJob


class AsyncLoop(threading.Thread):
    """A thread for running the asyncio event loop in background"""
    def __init__(self, maxsize=100):
        super().__init__()
        self._event_loop = asyncio.new_event_loop()
        self._maxsize = maxsize
        self.pending = queue.Queue()
        self.running = ConfinedSet(maxsize=self._maxsize)

    def run(self):
        asyncio.set_event_loop(self._event_loop)
        try:
            self._event_loop.run_forever()
        finally:
            # TODO: this finally block does not work
            # https://stackoverflow.com/questions/42291212
            # https://stackoverflow.com/questions/26148987
            # https://stackoverflow.com/questions/44684898
            # https://docs.python.org/3/library/signal.html
            self._event_loop.close()

    def stop(self):
        """Stop the event loop of this thread
        The event loop should be stopped by this thread,
        not by the main thread"""
        while self.running:
            ajob = self.running.pop()
            ajob.cancel()
            try:
                ajob.result()
            except asyncio.CancelledError:
                pass
        while self.pending.qsize():
            ajob = self.pending.get_nowait()
            ajob.future.set_exception(asyncio.CancelledError)
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)

    def submit(self, job_coro, callback=None):
        if self.running.is_full():
            ajob = AsyncJob(job_coro, callback=callback)
            self.pending.put_nowait(ajob)
        else:
            ajob = self._submit(job_coro, callback)
            self.running.add(ajob)
        return ajob

    def _submit(self, job_coro, callback=None):
        """Initialize a job, which is a coroutine with an optional callback"""
        # if not inspect.iscoroutine(job) and not asyncio.iscoroutine(job):
        #     raise TypeError('A coroutine object is required')
        fut = asyncio.run_coroutine_threadsafe(
            job_coro,
            loop=self._event_loop,
        )
        ajob = AsyncJob(job_coro, future=fut, callback=callback)
        fut.add_done_callback(callback_done(self, ajob))
        if callback is not None:
            fut.add_done_callback(callback)
        return ajob

    def submit_many(self, jobs_iter, callback=None):
        """Initialize multiple jobs, and then return corresponding futures"""
        return [self.submit(job, callback) for job in jobs_iter]

    def is_running(self):
        return bool(self.running)
