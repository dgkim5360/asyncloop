"""
Since `ConfinedMap` is a subclass of `collections.UserDict`,
the basic features of `UserDict` are not tested here,
but only the additional functionalities.
"""
import pytest

from asyncloop.map import ConfinedMap


def test_init():
    cmap = ConfinedMap(maxsize=5)
    assert cmap.maxsize == 5


def test_qsize():
    cmap = ConfinedMap(maxsize=5)
    assert cmap.qsize() == len(cmap) == 0
    cmap[1] = 10
    assert cmap.qsize() == len(cmap) == 1


def test_check_full():
    cmap = ConfinedMap(maxsize=1)
    assert cmap.is_full() is False

    cmap[1] = 10
    assert cmap.is_full() is True


def test_prevent_adding_when_full():
    cmap = ConfinedMap(maxsize=2)
    cmap[1] = 10
    cmap[2] = 20
    with pytest.raises(RuntimeError):
        cmap[3] = 30
