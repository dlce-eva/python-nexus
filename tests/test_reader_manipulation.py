"""Tests for nexus reading manipulation"""
import re


def test_add_taxa(nex):
    assert nex.data.ntaxa == 4
    nex.data.add_taxon('Elvis', ['1', '2'])
    assert nex.data.ntaxa == 5
    assert nex.data.matrix['Elvis'] == ['1', '2']
    assert 'Elvis' in nex.data.taxa
    assert 'Elvis' in nex.data.matrix
    expected_patterns = [
        r'^begin data;$',
        r'^\s+dimensions ntax=5 nchar=2;$',
        r'^\s+format datatype=standard gap=- symbols="012";$',
        r'^matrix$',
        r'^Simon\s+01$',
        r'^Louise\s+11$',
        r'^Betty\s+10$',
        r'^Harry\s+00$',
        r'^Elvis\s+12$',
        r'^\s+;$',
        r'^end;$',
    ]
    written = nex.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected


def test_delete_taxa(nex):
    assert nex.data.ntaxa == 4
    nex.data.del_taxon('Simon')
    assert nex.data.ntaxa == 3

    assert 'Simon' not in nex.data.taxa
    assert 'Simon' not in nex.data.matrix

    expected_patterns = [
        r'^begin data;$',
        r'^\s+dimensions ntax=3 nchar=2;$',
        r'^\s+format datatype=standard gap=- symbols="01";$',
        r'^matrix$',
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

    # should NOT be here
    assert re.search('^Simon\s+01$', written, re.MULTILINE) is None, \
        'Expected Taxon "Simon" to be Deleted'


def test_add_character(nex):
    assert nex.data.nchar == 2
    for taxon in nex.data.matrix:
        nex.data.matrix[taxon].append('9')
    expected_patterns = [
        r'^begin data;$',
        r'^\s+dimensions ntax=4 nchar=3;$',
        r'^\s+format datatype=standard gap=- symbols="019";$',
        r'^matrix$',
        r'^Simon\s+019$',
        r'^Louise\s+119$',
        r'^Betty\s+109$',
        r'^Harry\s+009$',
        r'^\s+;$',
        r'^end;$',
    ]
    written = nex.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected


def test_delete_character(nex):
    assert nex.data.nchar == 2
    for taxon in nex.data.matrix:
        nex.data.matrix[taxon].pop()
    expected_patterns = [
        r'^begin data;$',
        r'^\s+dimensions ntax=4 nchar=1;$',
        r'^\s+format datatype=standard gap=- symbols="01";$',
        r'^matrix$',
        r'^Simon\s+0$',
        r'^Louise\s+1$',
        r'^Betty\s+1$',
        r'^Harry\s+0$',
        r'^\s+;$',
        r'^end;$',
    ]
    written = nex.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected
