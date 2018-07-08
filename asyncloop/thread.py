import asyncio
import threading
import queue

from asyncloop.set import ConfinedSet
from asyncloop.job import PendingJob


class AsyncLoop(threading.Thread):
    """A thread for running the asyncio event loop in background."""
    def __init__(self, maxsize=100, daemon=True):
        super().__init__(daemon=daemon)
        self._event_loop = asyncio.new_event_loop()
        self._maxsize = maxsize
        self.pending = queue.Queue()
        self.running = ConfinedSet(maxsize=self._maxsize)
        self.done = set()

    def run(self):
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_forever()

    def stop(self):
        """Stop the event loop of this thread.

        The event loop should be stopped by this thread,
        not by the main thread"""
        while self.running:
            fut = self.running.pop()
            fut.cancel()
            try:
                fut.result()
            except asyncio.CancelledError:
                pass
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)

    def submit(self, job_coro, callback=None):
        """Check whether the running queue is full, and then
        convey the coroutine to the running or pending queue appropriately.

        It returns a PendingJob instance if the running queue is full,
        a concurrent.futures.Future instance otherwise."""
        if self.running.is_full():
            pjob = PendingJob(job_coro, callback=callback)
            self.pending.put_nowait(pjob)
            return pjob
        else:
            fut = self._submit(job_coro, callback)
            self.running.add(fut)
            return fut

    def submit_many(self, jobs_iter, callback=None):
        """Initialize multiple jobs, and then return corresponding futures.
        This method currently supports the identical callback to all jobs."""
        return [self.submit(job, callback) for job in jobs_iter]

    def is_running(self):
        return bool(self.running)

    def callback_default(self):
        def _clear(fut):
            if fut.done():
                self.done.add(fut)
                try:
                    self.running.remove(fut)
                    pjob = self.pending.get_nowait()
                except KeyError:
                    pass
                except queue.Empty:
                    pass
                else:
                    self.submit(pjob.job_coro, pjob.callback)
        return _clear

    def _submit(self, job_coro, callback=None):
        """Actual execution of a coroutine with an optional callback."""
        fut = asyncio.run_coroutine_threadsafe(
            job_coro,
            loop=self._event_loop,
        )
        fut.add_done_callback(self.callback_default())
        if callback is not None:
            fut.add_done_callback(callback)
        return fut
