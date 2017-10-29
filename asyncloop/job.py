import concurrent
import queue


def callback_done(aloop, ajob):
    def _clear(fut):
        if fut.done():
            try:
                aloop.running.remove(ajob)
                pending_ajob = aloop.pending.get_nowait()
            except KeyError:
                pass
            except queue.Empty:
                pass
            else:
                aloop.submit(pending_ajob.job_coro, pending_ajob.callback)
    return _clear


class AsyncJob:
    """A simple wrapper for concurrent.Future, currently not awaitable"""
    def __init__(self, job_coro, callback=None, future=None):
        self.job_coro = job_coro
        self.callback = callback
        self.future = future or concurrent.futures.Future()

    @property
    def state(self):
        return self.future._state

    def result(self):
        return self.future.result()

    def exception(self):
        return self.future.exception()

    def cancel(self):
        return self.future.cancel()

    def done(self):
        return self.future.done()

    def cancelled(self):
        return self.future.cancelled()
