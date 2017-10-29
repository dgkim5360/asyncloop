asyncloop
=========
*A Celery-like event loop with `asyncio` and no dependencies*

It runs an ``asyncio`` event loop in a separate thread, drives native coroutines within the loop, and then returns the future in an asynchronous manner. 

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
  aloop = AsyncLoop()  # <AsyncLoop(Thread-##, initial)>
  aloop.start()  # <AsyncLoop(Thread-##, started ##########)>

  # Submit a job and be free to work on
  # it returns an AsyncJob object, a simple wrapper of concurrent.Future
  ajob = aloop.submit(job_to_wait(10), callback)
  ajob  # <AsyncJob at 0x####>

  # After 10 seconds the callback activated
  # DONE: <Future at 0x#### state=finished returned int>
  # RESULT: 10

  # Get a result
  ret = ajob.result()  # 10

  # You MUST stop the aloop before exit or destroy
  aloop.stop()  # <AsyncLoop(Thread-##, stopped ##########)>

So far, that's all.
