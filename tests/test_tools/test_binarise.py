import re

import pytest

from nexus import NexusReader
from nexus.tools.binarise import binarise, _recode_to_binary


def test_Recode_To_Binary_error_on_integer():
    orig = {'Maori': 1, 'Dutch': '1', 'Latin': '1'}
    with pytest.raises(ValueError):
        _recode_to_binary(orig)


def test_Recode_To_Binary_error_on_badvalue():
    orig = {'Maori': None, 'Dutch': '1', 'Latin': '1'}
    with pytest.raises(ValueError):
        _recode_to_binary(orig)


@pytest.mark.parametrize(
    'input,expected',
    [
        (('1', '1', '1'), ('1', '1', '1')),
        (('1', '2', '1'), ('10', '01', '10')),
        (('1', '2', '3'), ('100', '010', '001')),
        (('0', '2', '1'), ('00', '01', '10')),
        (('?', '2', '1'), ('00', '01', '10')),
        (('-', '2', '1'), ('00', '01', '10')),
        (('1', '5', '9'), ('100', '010', '001')),
        (('1,3', '2', '3'), ('101', '010', '001')),
        (('1 3', '2', '3'), ('101', '010', '001')),
        (('A', 'B', 'C'), ('100', '010', '001')),
        (('A,B,C', 'B', 'C'), ('111', '010', '001')),
    ]
)
def test_recode_to_binary(input, expected):
    recoded = _recode_to_binary(dict(zip(['Maori', 'Dutch', 'Latin'], input)))
    assert recoded == dict(zip(['Maori', 'Dutch', 'Latin'], expected))


def test_Recode_To_Binary_absent_state_but_keep_zero():
    orig = {'Maori': '0', 'Dutch': '2', 'Latin': '1'}
    recoded = _recode_to_binary(orig, keep_zero=True)
    assert recoded['Maori'] == '100', recoded
    assert recoded['Dutch'] == '001', recoded
    assert recoded['Latin'] == '010', recoded


@pytest.fixture
def nex():
    res = NexusReader.from_string("""
        Begin data;
        Dimensions ntax=3 nchar=2;
        Format datatype=standard symbols="01" gap=-;
        Charstatelabels
            1 char1, 2 char2;
        Matrix
        Maori               14
        Dutch               25
        Latin               36
        ;""")
    return binarise(res)


def test_to_binary(nex):
    """Test Nexus -> Binary: Two Character"""
    expected = {
        'char1_0': {"Maori": '1', "Dutch": "0", "Latin": "0"},
        'char1_1': {"Maori": '0', "Dutch": "1", "Latin": "0"},
        'char1_2': {"Maori": '0', "Dutch": "0", "Latin": "1"},
        'char2_0': {"Maori": '1', "Dutch": "0", "Latin": "0"},
        'char2_1': {"Maori": '0', "Dutch": "1", "Latin": "0"},
        'char2_2': {"Maori": '0', "Dutch": "0", "Latin": "1"},
    }

    for char, data in expected.items():
        for taxon, exp_value in data.items():
            assert nex.data[char][taxon] == exp_value


def test_to_binary_nchar(nex):
    """Test Nexus -> Binary: Number of Characters"""
    assert len(nex.characters) == 6


def test_to_binary_symbollist(nex):
    """Test Nexus -> Binary: Update Symbol List"""
    # check symbol list was updated
    assert len(nex.symbols) == 2
    assert '1' in nex.symbols
    assert '0' in nex.symbols


def test_to_binary_nexus(nex):
    """Test Nexus -> Binary: Nexus"""
    nexus = nex.make_nexus(interleave=False)
    assert re.search(r"Dutch\s+010010", nexus)
    assert re.search(r"Maori\s+100100", nexus)
    assert re.search(r"Latin\s+001001", nexus)
