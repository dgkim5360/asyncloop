import asyncio
import time


async def simple_job(sleep_sec):
    await asyncio.sleep(sleep_sec)
    return sleep_sec


def test_init(aloop):
    assert aloop.is_alive()
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 0
    # assert len(aloop.finished) is 0
    # assert len(aloop.cancelled) is 0


def test_submit(aloop):
    aloop.submit(simple_job(.5))
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 1
    # assert len(aloop.finished) is 0
    # assert len(aloop.cancelled) is 0

    fut2 = aloop.submit(simple_job(1))
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 2
    # assert len(aloop.finished) is 0
    # assert len(aloop.cancelled) is 0

    fut2.cancel()
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 1
    # assert len(aloop.finished) is 0
    # assert len(aloop.cancelled) is 1

    time.sleep(.6)
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 0
    # assert len(aloop.finished) is 1
    # assert len(aloop.cancelled) is 1


def test_pending_jobs(aloop):
    ajobs = aloop.submit_many((simple_job(.5) for _ in range(10)))
    assert aloop.pending.qsize() is 5
    assert aloop.running.qsize() is 5
    # assert len(aloop.finished) is 0
    # assert len(aloop.cancelled) is 0

    ajob = ajobs[0]
    ajob.cancel()
    assert aloop.pending.qsize() is 4
    assert aloop.running.qsize() is 5
    # assert len(aloop.finished) is 0
    # assert len(aloop.cancelled) is 1

    aloop.submit(simple_job(1))
    assert aloop.pending.qsize() is 5
    assert aloop.running.qsize() is 5
    # assert len(aloop.finished) is 0
    # assert len(aloop.cancelled) is 1

    time.sleep(.55)
    assert aloop.pending.qsize() is 0
    assert aloop.running.qsize() is 5
    # assert len(aloop.finished) is 5
    # assert len(aloop.cancelled) is 1
