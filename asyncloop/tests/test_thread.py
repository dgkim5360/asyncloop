import asyncio
import collections
import time
import types
import pytest

from asyncloop.thread import AsyncLoop
from asyncloop.job import AsyncJob


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


@pytest.mark.xfail
def test_destroy_before_stop(aloop):
    """Currently if the program destroys asyncloop without stopping it,
    the program blocks forever to join the thread whose event loop is running
    forever."""
    assert False


def test_submit_a_job(aloop):
    ajob = aloop.submit(simple_job(.5))
    assert isinstance(ajob, AsyncJob)
    assert ajob.state == 'PENDING'
    time.sleep(.6)
    assert ajob.state == 'FINISHED'
    assert ajob.result() == .5


def test_submit_with_callback(aloop):
    ajob = aloop.submit(simple_job(.5), simple_callback)
    time.sleep(.6)
    # TODO: what to test?
    assert ajob.done()
    assert ajob.result() == .5


def test_cancel_a_submitted_job(aloop):
    ajob = aloop.submit(simple_job(600))
    assert not ajob.done()
    ajob.cancel()
    time.sleep(.01)
    assert ajob.cancelled()


def test_store_running_jobs(aloop):
    """TODO:
    Does it need job queue? or simple list/dict? asyncio.Queue?
    Does it need a separate storage depending on statuses?

    we might need
    a pending queue: FIFO queue seems good (No asyncio.Queue)
    a running list with size limit: maybe new list type needed

    TODO: handle destroy warning
    https://docs.python.org/3/library/asyncio-dev.html
    """
    assert aloop.running.qsize() is 0
    ajob1 = aloop.submit(simple_job(.5))
    ajob2 = aloop.submit(simple_job(600))
    assert aloop.running.qsize() is 2
    ajob2.cancel()
    time.sleep(.6)
    print(ajob1, ajob1.state)
    print(ajob2, ajob2.state)

    time.sleep(.01)
    assert aloop.running.qsize() is 0


def test_store_pending_jobs(aloop):
    ajobs = aloop.submit_many((simple_job(.2) for _ in range(5)))
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 5
    ajob = aloop.submit(simple_job(.2))
    assert aloop.pending.qsize() is 1
    assert aloop.running.qsize() is 5
    time.sleep(.3)


def test_submit_many(aloop):
    jobs = (simple_job(i*.2) for i in range(5))
    ajobs = aloop.submit_many(jobs, simple_callback)
    assert isinstance(ajobs, collections.Iterable)
    assert all(ajob.done() is False for ajob in ajobs)
    time.sleep(1)
    assert all(ajob.done() for ajob in ajobs)


def test_control_limit(aloop):
    """WLOG, assume the limit is set as 5"""
    ajobs = aloop.submit_many((simple_job(600) for _ in range(10)))
    assert aloop.pending.qsize() is 5
    assert aloop.running.qsize() is 5
    for ajob in ajobs:
        ajob.cancel()
    time.sleep(.01)


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
        yield from asyncio.sleep(.5)
        return .5

    @types.coroutine
    def gen_job2():
        yield from asyncio.sleep(.5)
        return .5

    ajob1 = aloop.submit(gen_job1())
    ajob2 = aloop.submit(gen_job2())
    assert ajob1.state == 'PENDING'
    assert ajob2.state == 'PENDING'
    time.sleep(.6)
    assert ajob1.done()
    assert ajob1.result() == .5
    assert ajob2.done()
    assert ajob2.result() == .5


def test_check_running_status(aloop):
    assert aloop.is_running() is False
    ajob = aloop.submit(simple_job(10))
    assert aloop.is_running() is True

    ajob.cancel()
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

    ajob = aloop.submit(simple_job(600))

    aloop.stop()
    assert ajob.state in ['CANCELLED_AND_NOTIFIED', 'CANCELLED']
    with pytest.raises(asyncio.CancelledError):
        ajob.result()


def test_stop_gracefully_pending_jobs():
    aloop = AsyncLoop(maxsize=1)
    aloop.start()

    ajob1 = aloop.submit(simple_job(600))
    ajob2 = aloop.submit(simple_job(600))

    aloop.stop()

    assert ajob2.state == 'FINISHED'
    with pytest.raises(asyncio.CancelledError):
        ajob2.result()


@pytest.mark.xfail
def test_run_independently_with_plain_asyncio_event_loop(aloop):
    """The asyncloop should be distinguished from other event loops"""
