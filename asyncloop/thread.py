import asyncio as aio
import inspect
import threading


class AsyncLoop(threading.Thread):
    """A thread for running the aio event loop in background"""
    def __init__(self):
        super().__init__()
        self._event_loop = aio.new_event_loop()

    def run(self):
        aio.set_event_loop(self._event_loop)
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
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)

    def submit_job(self, job_coro, callback=None):
        """Initialize a job, which is a coroutine with an optional callback"""
        # if not inspect.iscoroutine(job_coro) and not aio.iscoroutine(job_coro):
        #     raise TypeError('A coroutine object is required')
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
