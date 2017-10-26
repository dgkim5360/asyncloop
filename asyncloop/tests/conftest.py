import pytest

from asyncloop.thread import AsyncLoop


@pytest.fixture
def aloop():
    asyncloop = AsyncLoop()
    asyncloop.start()
    yield asyncloop
    asyncloop.stop()
