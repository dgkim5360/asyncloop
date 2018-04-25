import asyncio
import time


async def simple_job(sleep_sec):
    await asyncio.sleep(sleep_sec)
    return sleep_sec


def test_init(aloop):
    assert aloop.is_alive()
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 0


def test_submit(aloop):
    aloop.submit(simple_job(.2))
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 1

    fut2 = aloop.submit(simple_job(1))
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 2

    fut2.cancel()
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 1

    time.sleep(.3)
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 0


def test_pending_jobs(aloop):
    ajobs = aloop.submit_many((simple_job(.2) for _ in range(10)))
    assert aloop.pending.qsize() is 5
    assert aloop.running.qsize() is 5

    ajob = ajobs[0]
    ajob.cancel()
    assert aloop.pending.qsize() is 4
    assert aloop.running.qsize() is 5

    aloop.submit(simple_job(.2))
    assert aloop.pending.qsize() is 5
    assert aloop.running.qsize() is 5

    time.sleep(.3)
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 5
