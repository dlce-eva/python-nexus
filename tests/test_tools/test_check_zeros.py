import pytest

from nexus import NexusReader
from nexus.tools.check_zeros import check_zeros, remove_zeros


@pytest.fixture
def nex():
    nex = NexusReader()
    nex.read_string("""
        Begin data;
        Dimensions ntax=4 nchar=8;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        [                  01234567]
        Harry              01000000
        Simon              0010000-
        Betty              00010-0?
        Louise             000010?0
        ;""")
    return nex


@pytest.mark.parametrize(
    'kw,expected',
    [
        ({}, [0, 5, 6, 7]),
        ({'missing': ['-']}, [0, 5]),
        ({'absences': ['1', '0']}, [0, 1, 2,3, 4, 5,6, 7]),
    ]
)
def test_check_zeros(nex, kw, expected):
    assert expected == check_zeros(nex, **kw)


def test_remove_zeros(nex):
    new = remove_zeros(nex)
    assert new.data.nchar == 4
    assert new.data.matrix['Harry'] == ['1', '0', '0', '0']
    assert new.data.matrix['Simon'] == ['0', '1', '0', '0']
    assert new.data.matrix['Betty'] == ['0', '0', '1', '0']
    assert new.data.matrix['Louise'] == ['0', '0', '0', '1']
