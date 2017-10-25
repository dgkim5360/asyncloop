import asyncio as aio
import time
import types
import unittest

from asyncloop import AsyncLoop


class TestAsyncLoop(unittest.TestCase):
    """Detailed tests for AsyncLoop"""
    def setUp(self):
        self.asyncloop = AsyncLoop()
        self.asyncloop.start()

    def tearDown(self):
        self.asyncloop.stop()

    def test_asyncloop_must_warn_if_it_destoryes_without_stop(self):
        """EMPTY on purpose: to avoid <CTRL-C> escaping"""

    def test_asyncloop_should_raise_if_job_is_not_suitable(self):
        """Tests for constant, plain function"""
        def plain_function():
            return 'hello world!'

        with self.assertRaises(TypeError):
            self.asyncloop.submit_job(1)
        with self.assertRaises(TypeError):
            self.asyncloop.submit_job(plain_function())
        with self.assertRaises(TypeError):
            self.asyncloop.submit_job(plain_function)

    @unittest.skip('TODO')
    def test_asyncloop_should_raise_if_job_is_plain_generator(self):
        def plain_generator():
            for i in range(10):
                yield i

        with self.assertRaises(TypeError):
            fut = self.asyncloop.submit_job(plain_generator())
            print(fut)

    def test_asyncloop_should_accept_a_job_as_gen_based_coroutine(self):
        @aio.coroutine
        def gen_job():
            yield from aio.sleep(1)
            return 42

        fut = self.asyncloop.submit_job(gen_job())
        time.sleep(1)
        result = fut.result()
        self.assertEqual(result, 42)

        @types.coroutine
        def gen_job2():
            yield from aio.sleep(1)
            return 43

        fut = self.asyncloop.submit_job(gen_job2())
        time.sleep(1)
        result = fut.result()
        self.assertEqual(result, 43)

    @unittest.skip('NOTYET')
    def test_asyncloop_should_attach_id_to_future(self):
        """Celery-like feature: check how Celery does it"""

    @unittest.skip('NOTYET')
    def test_asyncloop_can_get_future_by_id(self):
        """Celery-like feature: check how Celery does it"""

    @unittest.skip('TODO')
    def test_asyncloop_can_check_it_is_idle(self):
        pass

    @unittest.skip('TODO')
    def test_asyncloop_can_check_it_is_running(self):
        pass

    @unittest.skip('NOTYET')
    def test_asyncloop_can_refuse_to_stop_with_pending_jobs(self):
        pass

    @unittest.skip('TODO')
    def test_asyncloop_must_store_jobs_submitted(self):
        pass


@unittest.skip('TODO')
class TestAsyncLoopWithAnotherLoop(unittest.TestCase):
    """Can distinguish AsyncLoop and plain asyncio event loop"""
    def setUp(self):
        self.asyncloop = AsyncLoop()
        self.asyncloop.start()
        time.sleep(.01)

    def tearDown(self):
        self.asyncloop.stop()


