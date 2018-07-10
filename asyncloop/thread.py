import asyncio
import threading
import time
import queue

from asyncloop.map import ConfinedMap
from asyncloop.job import PendingJob


class AsyncLoop(threading.Thread):
    """A thread for running the asyncio event loop in background."""
    def __init__(self, maxsize=100, daemon=True):
        super().__init__(daemon=daemon)
        self._event_loop = asyncio.new_event_loop()
        self._maxsize = maxsize
        self.pending = queue.Queue()
        self.running = ConfinedMap(maxsize=self._maxsize)
        self.done = set()

    def run(self):
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_forever()

    def stop(self):
        """Stop the event loop of this thread.

        The event loop should be stopped by this thread,
        not by the main thread"""
        while self.running:
            fut, coro = self.running.popitem()
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
            self.running[fut] = job_coro
            return fut

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
                    self.running.pop(fut)
                    pjob = self.pending.get_nowait()
                except KeyError:
                    pass
                except queue.Empty:
                    pass
                else:
                    self.submit(pjob.job_coro, pjob.callback)
        return _clear

    def monitor(self):
        """Make a curses window to show various jobs managed by the AsyncLoop.

        Note1:
        UNIX ONLY, since this method simply imports `curses` module, which is
        not available for Windows.

        Note2:
        This is an untested method, and I am not sure how to test this.
        """
        import curses

        stdscr = curses.initscr()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        width_split = curses.COLS//3-1
        win_done = curses.newwin(curses.LINES-1, width_split, 0, 0)
        win_running = curses.newwin(curses.LINES-1, width_split,
                                    0, width_split+1)
        win_pending = curses.newwin(curses.LINES-1, width_split,
                                    0, 2*width_split+1)
        stdscr.addstr(curses.LINES-1, 0,
                      'Monitoring started. Press Ctrl+C to stop.')
        stdscr.refresh()
        win_done.addstr(0, 0, 'DONE')
        win_pending.addstr(0, 0, 'PENDING')
        while True:
            try:
                win_done.addstr(1, 0,
                                f'{len(self.done)} jobs done')
                list_done = list(self.done)[:curses.LINES-3]
                for idx, job_done in enumerate(list_done, start=2):
                    fmt_str = f'{id(job_done):x} {job_done._state}'
                    win_done.addstr(idx, 0, fmt_str)
                win_done.refresh()

                win_running.clear()
                win_running.addstr(0, 0, 'RUNNING')
                win_running.addstr(1, 0,
                                   f'{self.running.qsize()} jobs running')
                list_running = list(self.running)[:curses.LINES-3]
                for idx, job_running in enumerate(list_running, start=2):
                    fmt_str = f'{id(job_running):x} {job_running._state}'
                    win_running.addstr(idx, 0, fmt_str)
                win_running.refresh()

                win_pending.clrtoeol()
                win_pending.addstr(1, 0,
                                   f'{self.pending.qsize()} jobs pending')
                win_pending.refresh()
                time.sleep(.1)
            except KeyboardInterrupt:
                break

        curses.nocbreak()
        curses.echo()
        curses.endwin()
