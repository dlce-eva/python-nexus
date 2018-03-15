"""Tests for DataHandler"""
import os
import re
import warnings
import unittest
from nexus import NexusReader
from nexus.reader import DataHandler

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')


class Test_DataHandler_parse_sites(unittest.TestCase):
    def test_simple(self):
        assert DataHandler()._parse_sites('123') == ['1', '2', '3']

    def test_multi(self):
        assert DataHandler()._parse_sites('1(12)') == ['1', '12']

    def test_comma(self):
        assert DataHandler()._parse_sites('123(4,5)56') == \
            ['1', '2', '3', '4,5', '5', '6']

    def test_sequence(self):
        assert DataHandler()._parse_sites("ACGTU?") == \
            ['A', 'C', 'G', 'T', 'U', '?']

    def test_maddison(self):
        assert DataHandler()._parse_sites('TAG;') == ['T', 'A', 'G']
    
    def test_extra_comma(self):
        assert DataHandler()._parse_sites('(T,A),C,G') == ['T,A', 'C', 'G']


class Test_DataHandler_SimpleNexusFormat(unittest.TestCase):
    expected = {
        'Harry': ['0', '0'],
        'Simon': ['0', '1'],
        'Betty': ['1', '0'],
        'Louise': ['1', '1'],
    }

    def setUp(self):
        self.nex = NexusReader(
            os.path.join(EXAMPLE_DIR, 'example.nex')
        )
    
    def test_repr(self):
        assert repr(self.nex.data) == "<NexusDataBlock: 2 characters from 4 taxa>"
        
    def test_block_find(self):
        assert 'data' in self.nex.blocks
        assert hasattr(self.nex, 'data')
        assert self.nex.data == self.nex.data

    def test_raw(self):
        assert self.nex.data.block == [
            'Begin data;',
            'Dimensions ntax=4 nchar=2;',
            'Format datatype=standard symbols="01" gap=-;',
            'Matrix',
            'Harry              00',
            'Simon              01',
            'Betty              10',
            'Louise             11',
            ';'
        ]
    
    def test_format_string(self):
        # did we get the expected tokens in the format string?
        expected = {'datatype': 'standard', 'gap': '-', 'symbols': '01'}
        for k, v in expected.items():
            assert self.nex.data.format[k] == v, \
                "%s should equal %s and not %s" % \
                (k, v, self.nex.data.format[k])
        # did we get the right number of tokens?
        assert len(self.nex.data.format) == len(expected)

    def test_taxa(self):
        # did we get the right taxa in the matrix?
        for taxon in self.expected:
            assert taxon in self.nex.data.matrix
        # did we get the right number of taxa in the matrix?
        assert self.nex.data.ntaxa == len(self.expected)
        assert self.nex.data.ntaxa == len(self.nex.data.taxa)

    def test_matrix(self):
        assert self.nex.data.nchar == 2
        for taxon, expected in self.expected.items():
            assert self.nex.data.matrix[taxon] == expected
            
    def test_characters(self):
        for site, data in self.nex.data.characters.items():
            for taxon, value in data.items():
                assert value == self.expected[taxon][site]
                
    def test_iterable(self):
        for taxon, block in self.nex.data:
            assert block == self.expected[taxon]

    def test_parse_format_line(self):
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
    
    def test_parse_format_line_returns_none(self):
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
        
        
    def test_write(self):
        expected_patterns = [
            '^begin data;$',
            '^\s+dimensions ntax=4 nchar=2;$',
            '^\s+format datatype=standard gap=- symbols="01";$',
            '^matrix$',
            '^Simon\s+01$',
            '^Louise\s+11$',
            '^Betty\s+10$',
            '^Harry\s+00$',
            '^\s+;$',
            '^end;$',
        ]
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected

    def test_get_site(self):
        for i in (0, 1):
            site_data = self.nex.data.characters[i]
            for taxon, value in site_data.items():
                assert self.expected[taxon][i] == value

    def test_incorrect_dimensions_warnings_ntaxa(self):
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

    def test_incorrect_dimensions_warnings_nchar(self):
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


class Test_DataHandler_InterleavedNexusFormat(unittest.TestCase):
    def test_interleave_matrix_parsing(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example3.nex'))
        assert nexus.data.ntaxa == 2 == len(nexus.data.taxa)
        assert nexus.data.nchar == 6
        for taxon, blocks in nexus.data:
            for i in range(0, nexus.data.nchar):
                assert blocks[i] == str(i), "Error for %s:%d" % (taxon, i)



class Test_DataHandler_AlternateNexusFormat(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))

    def test_block_find(self):
        assert 'data' in self.nex.blocks

    def test_ntaxa_recovery(self):
        # the alternate format has a distinct taxa and characters block, and
        # we need to estimate the number of taxa in a different way.
        assert self.nex.data.ntaxa == 4

    def test_format_string(self):
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
        assert self.nex.data.format is not None
        # did we get the expected tokens?
        for k, v in expected.items():
            assert self.nex.data.format[k] == v, \
                "%s should equal %s and not %s" % \
                (k, v, self.nex.data.format[k])
        # did we get the right number of tokens?
        assert len(self.nex.data.format) == len(expected)

    def test_taxa(self):
        expected = ['John', 'Paul', 'George', 'Ringo']
        # did we get the taxa right?
        for e in expected:
            assert e in self.nex.data.taxa, "%s should be in taxa" % e
        # did we get the number of taxa right?
        assert self.nex.data.ntaxa == len(expected) == len(self.nex.data.taxa)

    def test_data(self):
        # did we get the right amount of data?
        assert self.nex.data.nchar == 4
        # are all the characters parsed correctly?
        for k in self.nex.data.matrix:
            assert self.nex.data.matrix[k] == ['a', 'c', 't', 'g']


class Test_DataHandler_CharacterBlockNexusFormat(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(EXAMPLE_DIR, 'example-characters.nex')
        )

    def test_block_find(self):
        assert 'data' in self.nex.blocks

    def test_charblock_find(self):
        assert hasattr(self.nex.data, 'characters')

    def test_taxa(self):
        assert self.nex.data.ntaxa == 5

    def test_data(self):
        assert self.nex.data.nchar == 5

    def test_charlabels(self):
        assert self.nex.data.charlabels[0] == 'CHAR_A'
        assert self.nex.data.charlabels[1] == 'CHAR_B'
        assert self.nex.data.charlabels[2] == 'CHAR_C'
        assert self.nex.data.charlabels[3] == 'CHAR_D'
        assert self.nex.data.charlabels[4] == 'CHAR_E'

    def test_label_parsing(self):
        assert 'CHAR_A' in self.nex.data.characters
        assert 'CHAR_B' in self.nex.data.characters
        assert 'CHAR_C' in self.nex.data.characters
        assert 'CHAR_D' in self.nex.data.characters
        assert 'CHAR_E' in self.nex.data.characters

    def test_matrix(self):
        for taxon in ("A", "B", "C", "D", "E"):
            for index, expected_value in enumerate(("A", "B", "C", "D", "E")):
                assert self.nex.data.matrix[taxon][index] == expected_value

    def test_characters(self):
        for site in ("A", "B", "C", "D", "E"):
            # All sites in CHAR_A are state "A", and all in CHAR_B and "B" etc
            for t in ("A", "B", "C", "D", "E"):
                assert self.nex.data.characters["CHAR_%s" % site][t] == site
    
    def test_write(self):
        expected_patterns = [
            '^begin data;$',
            '^\s+dimensions ntax=5 nchar=5;$',
            '^\s+format gap=- missing=\?;$',
            '^\s+charstatelabels$',
            '^\s+1\s+CHAR_A,$',
            '^\s+2\s+CHAR_B,$',
            '^\s+3\s+CHAR_C,$',
            '^\s+4\s+CHAR_D,$',
            '^\s+5\s+CHAR_E$',
            '^matrix$',
            '^A\s+ABCDE$',
            '^B\s+ABCDE$',
            '^C\s+ABCDE$',
            '^D\s+ABCDE$',
            '^E\s+ABCDE$',
            '^\s+;$',
            '^end;$',
        ]
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected

