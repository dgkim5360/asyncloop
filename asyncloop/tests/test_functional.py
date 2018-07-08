import asyncio
import time


async def simple_job(sleep_sec):
    await asyncio.sleep(sleep_sec)
    return sleep_sec


def test_init(aloop):
    assert aloop.is_alive()
    assert len(aloop.done) == 0
    assert aloop.pending.qsize() == 0
    assert aloop.running.qsize() == 0


def test_submit(aloop):
    aloop.submit(simple_job(.2))
    assert len(aloop.done) == 0
    assert aloop.pending.qsize() == 0
    assert aloop.running.qsize() == 1

    fut2 = aloop.submit(simple_job(1))
    assert len(aloop.done) == 0
    assert aloop.pending.qsize() == 0
    assert aloop.running.qsize() == 2

    fut2.cancel()
    assert len(aloop.done) == 1
    assert aloop.pending.qsize() == 0
    assert aloop.running.qsize() == 1

    time.sleep(.3)
    assert len(aloop.done) == 2
    assert aloop.pending.qsize() == 0
    assert aloop.running.qsize() == 0


def test_pending_jobs(aloop):
    ajobs = aloop.submit_many((simple_job(.2) for _ in range(10)))
    assert len(aloop.done) == 0
    assert aloop.pending.qsize() == 5
    assert aloop.running.qsize() == 5

    ajob = ajobs[0]
    ajob.cancel()
    assert len(aloop.done) == 1
    assert aloop.pending.qsize() == 4
    assert aloop.running.qsize() == 5

    aloop.submit(simple_job(.2))
    assert len(aloop.done) == 1
    assert aloop.pending.qsize() == 5
    assert aloop.running.qsize() == 5

    time.sleep(.3)
    assert len(aloop.done) == 6
    assert aloop.pending.qsize() == 0
    assert aloop.running.qsize() == 5
