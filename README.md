# asyncloop

[![Build Status](https://travis-ci.org/dgkim5360/asyncloop.svg?branch=master)](https://travis-ci.org/dgkim5360/asyncloop)

*A Celery-like event loop with `asyncio` and no dependencies*

It runs an `asyncio` event loop in a separate daemon thread, drives native coroutines within the event loop, and then returns the future in an asynchronous manner.

### Example

This example sends 6000 simple HTTP GET requests with a job queue of size 30. The `monitor` method shows the process, which may be just an eye candy.

* The first column shows (id of future, state of the future), the finished jobs.
* The second column shows (id of future, state of the corresponding coroutine), the running jobs.
* The last column shows the number of pending jobs.

To serve the HTTP GET responses, the Nginx docker image is used.

<img src="https://cdn.rawgit.com/dgkim5360/asyncloop/master/examples/example-aiohttp-get.svg">

```shell
$ docker run --name ANY_NAME \
    -v /path/to/asyncloop/examples/nginx-staticfiles:/usr/share/nginx/html:ro \
    -d \
    -p 8080:80 \
    nginx
(venv) $ pip install aiohttp
(venv) $ python examples/aiohttp-get.py
```

Please note that the `monitor` method does not run in Windows OS, since it uses the `curses` module, which is available only in UNIX-like OS.

### Dependency

It requires Python 3.5+.

### Installation

```shell
$ git clone https://github.com/dgkim5360/asyncloop.git
$ cd asyncloop
asyncloop$ python setup.py install
```

### Getting started

```python
import asyncio as aio
import time

from asyncloop import AsyncLoop


# A simple job, which should be a native coroutine
async def job_to_wait(sleep_sec):
    await aio.sleep(sleep_sec)
    return sleep_sec


# A simple callback
def callback(fut):
    if fut.cancelled():
        print('CANCELLED:', fut)
    elif fut.done():
        print('DONE:', fut)
	print('RESULT:', fut.result()


# AsyncLoop starts
aloop = AsyncLoop(maxsize=5)
aloop.start()

# Submit a job and be free to work on
# it returns an concurrent.futures.Future object
fut = aloop.submit(job_to_wait(10), callback)

# After 10 seconds the callback activated
time.sleep(10)
# DONE: <Future at 0x#### state=finished returned int>
# RESULT: 10

# Get a result
assert fut.result() == 10

# Now the running queue (aloop.running) is empty!
# Submit more jobs
aloop.submit_many((job_to_wait(5) for _ in range(10)))

# AsyncLoop only runs 5 jobs and other jobs are pending
assert aloop.running.qsize() == 5
assert aloop.pending.qsize() == 5

# After 5 seconds so that 5 jobs done, pending job automatically starts
time.sleep(5)
assert aloop.running.qsize() == 5
assert aloop.pending.qsize() == 0
```

So far, that's all.
