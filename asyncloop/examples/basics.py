import time
import asyncio as aio

from asymplejobs.thread import Agent


if __name__ == '__main__':
    agent = Agent()
    agent.start()
    time.sleep(.1)

    easy_job = aio.sleep(3, result='hello')
    task = agent.init_job(easy_job)

    print('is task running?: ', task.running())
    print('is task done?: ', task.done())

    time.sleep(3)
    print('is task running?: ', task.running())
    print('is task done?: ', task.done())
    print('task gives: ', task.result())

    agent.stop()
