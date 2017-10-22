# asyncloop
*A Celery-like event loop with `asyncio` and no dependencies*

In a simple and easy manner, it runs an `asyncio` event loop in a separate thread and drives native coroutines within the loop.

# Installation
```
pip install asyncloop
```

# Get started
```python
import asyncio as aio

from asyncloop import AsyncLoop


# A simple job, which should be a native coroutine
async def job_to_wait(sleep_sec):
    await aio.sleep(sleep_sec)
    return sleep_sec


# A simple callback
def callback(fut):
    if fut.cancelled():
        print('CANCELLED: ', fut)
    elif fut.done():
        print('DONE: ', fut)
	print('RESULT: ', fut.result()


# AsyncLoop starts
aloop = AsyncLoop()  # <AsyncLoop(Thread-##, initial)>
aloop.start()  # <AsyncLoop(Thread-##, started ##########)>

# Submit a job and be free to work on
# it returns the concurrent.futures.Future object
fut = aloop.submit_job(job_to_wait(10), callback)
fut  # <Future at 0x#### state=pending>

# After 10 seconds the callback activated
DONE:  <Future at 0x#### state=finished returned int>
RESULT: 10

# Get a result
ret = fut.result()  # 10

# You MUST stop the aloop before exit or destroy
aloop.stop()  # <AsyncLoop(Thread-##, stopped ##########)>
```
So far, that's all.

`submit_job`, which takes a job as a native coroutine and callback, returns a `concurrent.futures.Future` object.

Also you may use `submit_jobs` with an iterable of coroutines and then it returns a list of `Future`s.
