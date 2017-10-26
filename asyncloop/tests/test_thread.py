import asyncio
import collections
import concurrent
import pytest
import time
import types

from asyncloop.thread import AsyncLoop


async def job_to_wait(sleep_sec):
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
    fut = aloop.submit(job_to_wait(.5))
    assert isinstance(fut, concurrent.futures.Future)
    assert fut._state == 'PENDING'
    time.sleep(.8)
    assert fut._state == 'FINISHED'
    assert fut.result() == .5


def test_submit_with_callback(aloop):
    fut = aloop.submit(job_to_wait(.5), simple_callback)
    time.sleep(.6)
    # TODO: what to test?
    assert fut.done()
    assert fut.result() == .5


def test_cancel_a_submitted_job(aloop):
    fut = aloop.submit(job_to_wait(600))
    assert not fut.done()
    fut.cancel()
    time.sleep(.01)
    assert fut.cancelled()


@pytest.mark.xfail
def test_store_futures(aloop):
    """TODO:
    Does it need job queue? or simple list/dict? asyncio.Queue?
    Does it need separate storage depending on statuses?
    """
    fut = aloop.submit(job_to_wait(600))
    assert len(aloop) == 1
    assert len(aloop.running) == 1
    assert len(aloop.pending) == 0
    assert aloop.jobs[fut] == fut
    fut.cancel()


def test_submit_many(aloop):
    jobs = (job_to_wait(i*.5) for i in range(1, 10))
    futs = aloop.submit_many(jobs, simple_callback)
    assert isinstance(futs, collections.Iterable)
    assert all(fut.done() is False for fut in futs)
    time.sleep(6)
    assert all(fut.done() for fut in futs)


@pytest.mark.xfail
def test_control_limit(aloop):
    """WLOG, assume the limit is set as 50"""
    futs = aloop.submit_many((job_to_wait(600) for _ in range(100)))
    assert len(aloop.running) == 50
    assert len(aloop.pending) == 50
    assert len(aloop) == 100
    for fut in futs:
        fut.cancel()


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

    fut1 = aloop.submit(gen_job1())
    fut2 = aloop.submit(gen_job2())
    assert fut1._state == 'PENDING'
    assert fut2._state == 'PENDING'
    time.sleep(.6)
    assert fut1.done()
    assert fut1.result() == .5
    assert fut2.done()
    assert fut2.result() == .5


@pytest.mark.xfail
def test_check_idle_status(aloop):
    pass


@pytest.mark.xfail
def test_check_running_status(aloop):
    pass


@pytest.mark.xfail
def test_attach_id_to_future(aloop):
    """Is it necessary?"""


@pytest.mark.xfail
def test_get_future_by_id(aloop):
    """Is it necessary?"""


@pytest.mark.xfail
def test_store_submitted_jobs(aloop):
    pass


@pytest.mark.xfail
def test_stop_gracefully(aloop):
    """When the asyncloop.stop() called with pending jobs,
    it should cancel all and then stop."""


@pytest.mark.xfail
def test_run_independently_with_plain_asyncio_event_loop(aloop):
    """The asyncloop should be distinguished from other event loops"""
