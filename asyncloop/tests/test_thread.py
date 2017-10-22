import unittest
import time

from asyncloop import AsyncLoop


class TestAsyncLoop(unittest.TestCase):
    """Tests for error cases of AsyncLoop"""
    def setUp(self):
        self.async_loop = AsyncLoop()
        self.async_loop.start()
        time.sleep(.01)

    def tearDown(self):
        self.async_loop.stop()

    @unittest.skip('TODO')
    def test_async_loop_must_warn_if_it_destoryes_without_stop(self):
        """TODO: to avoid <CTRL-C> escaping"""

    def test_async_loop_raise_if_job_is_not_a_coroutine(self):
        def not_a_job():
            return 'hello world!'

        with self.assertRaises(TypeError):
            self.async_loop.submit_job(1)
        with self.assertRaises(TypeError):
            self.async_loop.submit_job(not_a_job())
        with self.assertRaises(TypeError):
            self.async_loop.submit_job(not_a_job)

        def not_a_job():
            for i in range(10):
                yield i

        with self.assertRaises(TypeError):
            self.async_loop.submit_job(not_a_job())
