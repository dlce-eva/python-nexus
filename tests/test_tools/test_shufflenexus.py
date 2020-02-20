import pytest

from nexus import NexusWriter
from nexus.tools.shufflenexus import shufflenexus


def test_output(nex2):
    nexus_obj = shufflenexus(nex2)
    assert isinstance(nexus_obj, NexusWriter)


def test_exception_resample_noninteger(nex2):
    with pytest.raises(ValueError):
        shufflenexus(nex2, 'a')


def test_exception_resample_badinteger(nex2):
    with pytest.raises(ValueError):
        shufflenexus(nex2, 0)


def test_exception_resample_negativeinteger(nex2):
    with pytest.raises(ValueError):
        shufflenexus(nex2, -1)


def test_resample_1(nex2):
    nexus_obj = shufflenexus(nex2, 1)
    assert len(nexus_obj.characters) == 1
    assert sorted(nexus_obj.taxa) == \
        ['George', 'John', 'Paul', 'Ringo']


def test_resample_10(nex2):
    nexus_obj = shufflenexus(nex2, 10)
    assert len(nexus_obj.characters) == 10
    assert sorted(nexus_obj.taxa) == \
        ['George', 'John', 'Paul', 'Ringo']


def test_resample_100(nex2):
    nexus_obj = shufflenexus(nex2, 100)
    assert len(nexus_obj.characters) == 100
    assert sorted(nexus_obj.taxa) == \
        ['George', 'John', 'Paul', 'Ringo']
