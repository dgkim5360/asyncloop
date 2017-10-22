import threading
import inspect
import asyncio as aio


class AsyncLoop(threading.Thread):
    """A thread for running the aio event loop in background"""
    def run(self):
        self._event_loop = aio.new_event_loop()
        aio.set_event_loop(self._event_loop)
        self._event_loop.run_forever()

    def stop(self):
        """Stop the event loop of this thread"""
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)

    def submit_job(self, job_coro, callback=None):
        """Initializer a job, which is a coroutine with an optional callback"""
        if not inspect.iscoroutine(job_coro):
            raise TypeError('A coroutine object is required')
        fut = aio.run_coroutine_threadsafe(
            job_coro,
            loop=self._event_loop,
        )
        if callback is not None:
            fut.add_done_callback(callback)
        return fut

    def submit_jobs(self, jobs_iter, callback=None):
        """Initialize multiple jobs, and then return corresponding futures"""
        return [self.submit_job(job, callback) for job in jobs_iter]
