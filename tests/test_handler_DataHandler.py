"""Tests for DataHandler"""
import re
import warnings

import pytest

from nexus import NexusReader
from nexus.reader import DataHandler


@pytest.mark.parametrize(
    'input,expected',
    [
        ('123', ['1', '2', '3']),
        ('1(12)', ['1', '12']),
        ('123(4,5)56', ['1', '2', '3', '4,5', '5', '6']),
        ("ACGTU?", ['A', 'C', 'G', 'T', 'U', '?']),
        ('TAG;', ['T', 'A', 'G']),
        ('(T,A),C,G', ['T,A', 'C', 'G']),
    ]
)
def test_DataHandler_parse_sites(input, expected):
    assert DataHandler()._parse_sites(input) == expected


expected = {
    'Harry': ['0', '0'],
    'Simon': ['0', '1'],
    'Betty': ['1', '0'],
    'Louise': ['1', '1'],
}

def test_repr(nex):
    assert repr(nex.data) == "<NexusDataBlock: 2 characters from 4 taxa>"

def test_block_find(nex):
    assert 'data' in nex.blocks
    assert hasattr(nex, 'data')
    assert nex.data == nex.data

def test_raw(nex):
    assert nex.data.block == [
        'Begin data;',
        'Dimensions ntax=4 nchar=2;',
        'Format datatype=standard symbols="01" gap=-;',
        'Matrix',
        'Harry              00',
        'Simon              01',
        'Betty              10',
        'Louise             11',
        ';',
        'End;'
    ]


def test_format_string(nex):
    # did we get the expected tokens in the format string?
    expected = {'datatype': 'standard', 'gap': '-', 'symbols': '01'}
    for k, v in expected.items():
        assert nex.data.format[k] == v, \
            "%s should equal %s and not %s" % \
            (k, v, nex.data.format[k])
    # did we get the right number of tokens?
    assert len(nex.data.format) == len(expected)


def test_taxa(nex):
    # did we get the right taxa in the matrix?
    for taxon in expected:
        assert taxon in nex.data.matrix
    # did we get the right number of taxa in the matrix?
    assert nex.data.ntaxa == len(expected)
    assert nex.data.ntaxa == len(nex.data.taxa)


def test_matrix(nex):
    assert nex.data.nchar == 2
    for taxon, ex in expected.items():
        assert nex.data.matrix[taxon] == ex


def test_characters(nex):
    for site, data in nex.data.characters.items():
        for taxon, value in data.items():
            assert value == expected[taxon][site]


def test_characters_cached(nex):
    assert nex.data.characters == nex.data._characters


def test_iterable(nex):
    for taxon, block in nex.data:
        assert block == expected[taxon]


def test_parse_format_line():
    d = DataHandler()
    f = d.parse_format_line('Format datatype=standard gap=- symbols="01";')
    assert f['datatype'] == 'standard', \
        "Expected 'standard', but got '%s'" % f['datatype']
    assert f['symbols'] == '01', \
        "Expected '01', but got '%s'" % f['symbols']
    assert f['gap'] == '-', \
        "Expected 'gap', but got '%s'" % f['gap']

    fmt = 'FORMAT datatype=RNA missing=? symbols="ACGU" labels interleave;'
    f = d.parse_format_line(fmt)
    assert f['datatype'] == 'rna', \
        "Expected 'rna', but got '%s'" % f['datatype']
    assert f['missing'] == '?', \
        "Expected '?', but got '%s'" % f['missing']
    assert f['symbols'] == 'acgu', \
        "Expected 'acgu', but got '%s'" % f['symbols']
    assert f['labels'] is True, \
        "Expected <True>, but got '%s'" % f['labels']
    assert f['interleave'] is True, \
        "Expected <True>, but got '%s'" % f['interleave']


def test_parse_format_line_returns_none():
    d = DataHandler()
    assert d.parse_format_line('#NEXUS ') is None
    assert d.parse_format_line('') is None
    assert d.parse_format_line('Begin data;') is None
    assert d.parse_format_line('Dimensions ntax=4 nchar=2;') is None
    assert d.parse_format_line('Matrix') is None
    assert d.parse_format_line('Harry              00') is None
    assert d.parse_format_line('Simon              01') is None
    assert d.parse_format_line('Betty              10') is None
    assert d.parse_format_line('Louise             11') is None
    assert d.parse_format_line('    ;') is None
    assert d.parse_format_line('End;') is None


def test_write(nex):
    expected_patterns = [
        r'^begin data;$',
        r'^\s+dimensions ntax=4 nchar=2;$',
        r'^\s+format datatype=standard gap=- symbols="01";$',
        r'^matrix$',
        r'^Simon\s+01$',
        r'^Louise\s+11$',
        r'^Betty\s+10$',
        r'^Harry\s+00$',
        r'^\s+;$',
        r'^end;$',
    ]
    written = nex.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected


def test_get_site(nex):
    for i in (0, 1):
        site_data = nex.data.characters[i]
        for taxon, value in site_data.items():
            assert expected[taxon][i] == value


def test_incorrect_dimensions_warnings_ntaxa():
    nex = NexusReader()
    with warnings.catch_warnings(record=True) as w:
        nex.read_string(
            """Begin data;
            Dimensions ntax=5 nchar=1;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              1
            ;""")
        assert len(w) == 1, 'Expected 1 warning, got %r' % w
        assert issubclass(w[-1].category, UserWarning)
        assert "Expected" in str(w[-1].message)
        assert nex.data.nchar == 1


def test_incorrect_dimensions_warnings_nchar():
    with warnings.catch_warnings(record=True) as w:
        nex = NexusReader()
        nex.read_string(
            """Begin data;
            Dimensions ntax=1 nchar=5;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              1
            ;""")
        assert len(w) == 1, 'Expected 1 warning, got %r' % w
        assert issubclass(w[-1].category, UserWarning)
        assert "Expected" in str(w[-1].message)
        assert nex.data.nchar == 1


def test_interleave_matrix_parsing(examples):
    nexus = NexusReader(str(examples / 'example3.nex'))
    assert nexus.data.ntaxa == 2 == len(nexus.data.taxa)
    assert nexus.data.nchar == 6
    for taxon, blocks in nexus.data:
        for i in range(0, nexus.data.nchar):
            assert blocks[i] == str(i), "Error for %s:%d" % (taxon, i)


def test_block_find2(nex2):
    assert 'data' in nex2.blocks


def test_ntaxa_recovery(nex2):
    # the alternate format has a distinct taxa and characters block, and
    # we need to estimate the number of taxa in a different way.
    assert nex2.data.ntaxa == 4


def test_format_string2(nex2):
    expected = {
        'datatype': 'dna',
        'missing': '?',
        'gap': '-',
        'symbols': 'atgc',
        'labels': 'left',
        'transpose': 'no',
        'interleave': 'yes',
    }
    # did we manage to extract some format string at all?
    assert nex2.data.format is not None
    # did we get the expected tokens?
    for k, v in expected.items():
        assert nex2.data.format[k] == v, \
            "%s should equal %s and not %s" % \
            (k, v, nex2.data.format[k])
    # did we get the right number of tokens?
    assert len(nex2.data.format) == len(expected)


def test_taxa2(nex2):
    expected = ['John', 'Paul', 'George', 'Ringo']
    # did we get the taxa right?
    for e in expected:
        assert e in nex2.data.taxa, "%s should be in taxa" % e
    # did we get the number of taxa right?
    assert nex2.data.ntaxa == len(expected) == len(nex2.data.taxa)


def test_data(nex2):
    # did we get the right amount of data?
    assert nex2.data.nchar == 4
    # are all the characters parsed correctly?
    for k in nex2.data.matrix:
        assert nex2.data.matrix[k] == ['a', 'c', 't', 'g']


def test_block_findc(nexc):
    assert 'data' in nexc.blocks


def test_charblock_find(nexc):
    assert hasattr(nexc.data, 'characters')


def test_taxac(nexc):
    assert nexc.data.ntaxa == 5


def test_datac(nexc):
    assert nexc.data.nchar == 5


def test_charlabels(nexc):
    assert nexc.data.charlabels[0] == 'CHAR_A'
    assert nexc.data.charlabels[1] == 'CHAR_B'
    assert nexc.data.charlabels[2] == 'CHAR_C'
    assert nexc.data.charlabels[3] == 'CHAR_D'
    assert nexc.data.charlabels[4] == 'CHAR_E'


def test_label_parsing(nexc):
    assert 'CHAR_A' in nexc.data.characters
    assert 'CHAR_B' in nexc.data.characters
    assert 'CHAR_C' in nexc.data.characters
    assert 'CHAR_D' in nexc.data.characters
    assert 'CHAR_E' in nexc.data.characters


def test_matrixc(nexc):
    for taxon in ("A", "B", "C", "D", "E"):
        for index, expected_value in enumerate(("A", "B", "C", "D", "E")):
            assert nexc.data.matrix[taxon][index] == expected_value


def test_charactersc(nexc):
    for site in ("A", "B", "C", "D", "E"):
        # All sites in CHAR_A are state "A", and all in CHAR_B and "B" etc
        for t in ("A", "B", "C", "D", "E"):
            assert nexc.data.characters["CHAR_%s" % site][t] == site


def test_writec(nexc):
    expected_patterns = [
        r'^begin data;$',
        r'^\s+dimensions ntax=5 nchar=5;$',
        r'^\s+format gap=- missing=\?;$',
        r'^\s+charstatelabels$',
        r'^\s+1\s+CHAR_A,$',
        r'^\s+2\s+CHAR_B,$',
        r'^\s+3\s+CHAR_C,$',
        r'^\s+4\s+CHAR_D,$',
        r'^\s+5\s+CHAR_E$',
        r'^matrix$',
        r'^A\s+ABCDE$',
        r'^B\s+ABCDE$',
        r'^C\s+ABCDE$',
        r'^D\s+ABCDE$',
        r'^E\s+ABCDE$',
        r'^\s+;$',
        r'^end;$',
    ]
    written = nexc.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected
