import pytest

from asyncloop.thread import AsyncLoop


@pytest.fixture
def aloop():
    asyncloop = AsyncLoop(maxsize=5)
    asyncloop.start()
    return asyncloop
