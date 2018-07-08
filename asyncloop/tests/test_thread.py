import asyncio
import collections
import time
import types
import concurrent

import pytest

from asyncloop.thread import AsyncLoop


async def simple_job(sleep_sec):
    await asyncio.sleep(sleep_sec)
    return sleep_sec


def simple_callback(fut):
    print('STATE: ', fut._state)
    if fut.cancelled():
        print('CANCELLED: ', fut)
    elif fut.done():
        print('DONE: ', fut)
        print('RESULT: ', fut.result())


def test_init_and_destroy():
    aloop = AsyncLoop()
    assert isinstance(aloop._event_loop, asyncio.AbstractEventLoop)
    assert not aloop.is_alive()

    aloop.start()
    assert aloop.is_alive()
    assert aloop._event_loop.is_running()

    aloop.stop()
    time.sleep(.01)
    assert not aloop._event_loop.is_running()
    assert not aloop.is_alive()


def test_cancel_running_jobs_when_stopped():
    aloop = AsyncLoop()
    aloop.start()

    fut1 = aloop.submit(simple_job(.2))
    fut2 = aloop.submit(simple_job(.2))
    fut3 = aloop.submit(simple_job(.2))
    assert fut1._state == 'PENDING'
    assert fut2._state == 'PENDING'
    assert fut3._state == 'PENDING'

    aloop.stop()
    target_states = ('CANCELLED', 'CANCELLED_AND_NOTIFIED')
    assert fut1._state in target_states
    assert fut2._state in target_states
    assert fut3._state in target_states


def test_submit_a_job(aloop):
    fut = aloop.submit(simple_job(.2))
    assert isinstance(fut, concurrent.futures.Future)
    assert fut._state == 'PENDING'
    time.sleep(.3)
    assert fut._state == 'FINISHED'
    assert fut.result() == .2


def test_submit_a_job_with_callback(aloop):
    fut = aloop.submit(simple_job(.2), simple_callback)
    time.sleep(.3)
    assert fut.done()
    assert fut.result() == .2


def test_cancel_a_submitted_job(aloop):
    fut = aloop.submit(simple_job(600))
    assert not fut.done()
    fut.cancel()
    time.sleep(.01)
    assert fut.cancelled()


def test_store_running_jobs(aloop):
    assert aloop.running.qsize() == 0
    fut1 = aloop.submit(simple_job(.2))
    fut2 = aloop.submit(simple_job(600))
    assert aloop.running.qsize() == 2
    assert fut1._state == 'PENDING'
    assert fut2._state == 'PENDING'

    fut2.cancel()
    assert fut2._state in ('CANCELLED', 'CANCELLED_AND_NOTIFIED')
    time.sleep(.3)
    assert aloop.running.qsize() == 0


def test_store_pending_jobs(aloop):
    aloop.submit_many((simple_job(.2) for _ in range(5)))
    assert aloop.pending.qsize() == 0
    assert aloop.running.qsize() == 5

    aloop.submit(simple_job(.2))
    assert aloop.pending.qsize() == 1
    assert aloop.running.qsize() == 5


def test_store_processed_jobs(aloop):
    aloop.submit_many((simple_job(.2) for _ in range(5)))
    assert len(aloop.done) == 0

    time.sleep(.3)
    assert len(aloop.done) == 5


def test_submit_many(aloop):
    jobs = (simple_job(.2) for i in range(5))
    futs = aloop.submit_many(jobs, simple_callback)
    assert isinstance(futs, collections.Iterable)

    assert all(fut.done() is False for fut in futs)
    time.sleep(.3)
    assert all(fut.done() for fut in futs)


def test_control_limit(aloop):
    """WLOG, assume the limit is set as 5.

    TODO: handle destroy warning
    https://docs.python.org/3/library/asyncio-dev.html
    """
    aloop.submit_many((simple_job(60) for _ in range(10)))
    assert aloop.pending.qsize() == 5
    assert aloop.running.qsize() == 5


def test_raise_typeerror_for_plain_function_and_constant(aloop):
    def plain_func():
        return 'hello world'

    with pytest.raises(TypeError):
        aloop.submit(plain_func())
    with pytest.raises(TypeError):
        aloop.submit(plain_func)


@pytest.mark.xfail
def test_raise_typeerror_for_plain_generator(aloop):
    def plain_gen():
        return (i for i in range(10))

    with pytest.raises(TypeError):
        aloop.submit(plain_gen())


def test_accept_generator_based_coroutine(aloop):
    @asyncio.coroutine
    def gen_job1():
        yield from asyncio.sleep(.2)
        return .2

    @types.coroutine
    def gen_job2():
        yield from asyncio.sleep(.2)
        return .2

    fut1 = aloop.submit(gen_job1())
    fut2 = aloop.submit(gen_job2())
    assert fut1._state == 'PENDING'
    assert fut2._state == 'PENDING'
    time.sleep(.3)
    assert fut1.done()
    assert fut1.result() == .2
    assert fut2.done()
    assert fut2.result() == .2


def test_check_running_status(aloop):
    assert aloop.is_running() is False
    fut = aloop.submit(simple_job(10))
    assert aloop.is_running() is True

    fut.cancel()
    time.sleep(.01)
    assert aloop.is_running() is False


@pytest.mark.xfail
def test_attach_id_to_future(aloop):
    """Is it necessary?"""


@pytest.mark.xfail
def test_get_future_by_id(aloop):
    """Is it necessary?"""


def test_stop_gracefully_running_jobs():
    """When the asyncloop.stop() called with pending jobs,
    it should cancel all and then stop."""
    aloop = AsyncLoop(maxsize=5)
    aloop.start()

    fut = aloop.submit(simple_job(60))

    aloop.stop()
    assert fut._state in ('CANCELLED_AND_NOTIFIED', 'CANCELLED')
    with pytest.raises(asyncio.CancelledError):
        fut.result()


@pytest.mark.xfail
def test_run_independently_with_plain_asyncio_event_loop(aloop):
    """The asyncloop should be distinguished from other event loops"""
