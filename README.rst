asyncloop
=========
*A Celery-like event loop with `asyncio` and no dependencies*

It runs an ``asyncio`` event loop in a separate daemon thread, drives native coroutines within the event loop, and then returns the future in an asynchronous manner.

Dependency
----------
It requires Python 3.5+.

Installation
------------

::

  $ git clone https://github.com/dgkim5360/asyncloop.git
  $ cd asyncloop
  asyncloop$ python setup.py install

Getting started
---------------

::

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

So far, that's all.
