import unittest
import collections
import time
import concurrent
import asyncio as aio

from asyncloop import AsyncLoop


async def job_to_wait(sleep_sec):
    """A test job, which is just to wait"""
    await aio.sleep(sleep_sec)
    return sleep_sec


def callback(fut):
    """A test callback function, which is just to print"""
    if fut.cancelled():
        print('CANCELLED: ', fut)
    elif fut.done():
        print('DONE: ', fut)
        print('RESULT: ', fut.result())


class TestInit(unittest.TestCase):
    """Let's start"""
    def test_init_and_then_destory(self):
        """Check various statuses of the async_loop"""
        self.async_loop = AsyncLoop()
        self.assertFalse(self.async_loop.is_alive())

        self.async_loop.start()
        time.sleep(.01)  # TODO: time.sleep seems inappropriate
        self.assertTrue(self.async_loop.is_alive())
        self.assertTrue(self.async_loop._event_loop.is_running())

        self.async_loop.stop()
        time.sleep(.01)
        self.assertFalse(self.async_loop.is_alive())
        self.assertFalse(self.async_loop._event_loop.is_running())


class TestBasic(unittest.TestCase):
    """Basic functionalities, end-to-end scenario"""
    def setUp(self):
        self.async_loop = AsyncLoop()
        self.async_loop.start()
        time.sleep(.01)  # give time to start the thread

    def tearDown(self):
        self.async_loop.stop()
        time.sleep(.01)  # give time to stop the thread

    def test_async_loop_must_have_an_event_loop_as_attribute(self):
        self.assertTrue(hasattr(self.async_loop, '_event_loop'))
        self.assertIsInstance(self.async_loop._event_loop,
                              aio.AbstractEventLoop)

    def test_async_loop_event_loop_must_be_running(self):
        self.assertTrue(self.async_loop._event_loop.is_running())

    def test_async_loop_can_submit_a_job(self):
        fut = self.async_loop.submit_job(job_to_wait(1))
        self.assertIsInstance(fut, concurrent.futures.Future)
        self.assertEqual(fut._state, 'PENDING')
        time.sleep(1.1)
        self.assertEqual(fut._state, 'FINISHED')
        self.assertEqual(fut.result(), 1)

    def test_async_loop_can_submit_two_jobs(self):
        future1 = self.async_loop.submit_job(job_to_wait(1))
        future2 = self.async_loop.submit_job(job_to_wait(2))

        print(future1, future2)
        self.assertFalse(future1.done())
        self.assertFalse(future2.done())

        time.sleep(1.2)
        self.assertTrue(future1.done())
        self.assertFalse(future2.done())
        self.assertEqual(future1.result(), 1)

        time.sleep(1)
        self.assertTrue(future2.done())
        self.assertEqual(future2.result(), 2)

    def test_async_loop_can_submit_a_job_with_a_callback(self):
        self.async_loop.submit_job(job_to_wait(1), callback)
        time.sleep(1.1)

    def test_async_loop_can_cancel_a_job(self):
        fut = self.async_loop.submit_job(job_to_wait(60), callback)

        self.assertFalse(fut.done())
        fut.cancel()
        time.sleep(.1)
        self.assertTrue(fut.cancelled())

    def test_async_loop_can_submit_jobs(self):
        jobs = (job_to_wait(i*.5) for i in range(1, 5))
        futs = self.async_loop.submit_jobs(jobs, callback)

        self.assertIsInstance(futs, collections.Iterable)
        self.assertTrue(all(fut.done() is False for fut in futs))
        time.sleep(3)  # wait for all jobs to be done
        self.assertTrue(all(fut.done() for fut in futs))
