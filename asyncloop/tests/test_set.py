import pytest

from asyncloop.set import ConfinedSet


def test_init():
    cset = ConfinedSet(maxsize=5)
    assert cset.maxsize == 5

    cset.add(1)
    assert len(cset) == 1


def test_prevent_initial_data_too_large():
    with pytest.raises(ValueError):
        cset = ConfinedSet([1, 2, 3, 4, 5, 6, 7], maxsize=5)


def test_prevent_adding_when_full():
    cset = ConfinedSet(data=[1, 2, 3, 4, 5], maxsize=5)
    with pytest.raises(RuntimeError):
        cset.add(6)


def test_remove():
    cset = ConfinedSet(data=(1, 2, 3), maxsize=5)
    cset.remove(2)
    assert len(cset) == 2
    assert cset.qsize() == len(cset)
    assert cset._data == set((1, 3))

    with pytest.raises(KeyError):
        cset.remove(5)
