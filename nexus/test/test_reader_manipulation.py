"""Tests for nexus reading manipulation"""
import os
import re
import unittest
from nexus import NexusReader

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')

class Test_Manipulation_Data(unittest.TestCase):
    """Test the manipulation of data in the NexusReader"""

    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))

    def test_add_taxa(self):
        assert self.nex.data.ntaxa == 4
        self.nex.data.add_taxon('Elvis', ['1', '2'])
        assert self.nex.data.ntaxa == 5
        assert self.nex.data.matrix['Elvis'] == ['1', '2']
        assert 'Elvis' in self.nex.data.taxa
        assert 'Elvis' in self.nex.data.matrix
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
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected
        
    def test_delete_taxa(self):
        assert self.nex.data.ntaxa == 4
        self.nex.data.del_taxon('Simon')
        assert self.nex.data.ntaxa == 3

        assert 'Simon' not in self.nex.data.taxa
        assert 'Simon' not in self.nex.data.matrix

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
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected

        # should NOT be here
        assert re.search('^Simon\s+01$', written, re.MULTILINE) is None, \
            'Expected Taxon "Simon" to be Deleted'

    def test_add_character(self):
        assert self.nex.data.nchar == 2
        for taxon in self.nex.data.matrix:
            self.nex.data.matrix[taxon].append('9')
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
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected
            
    def test_delete_character(self):
        assert self.nex.data.nchar == 2
        for taxon in self.nex.data.matrix:
            self.nex.data.matrix[taxon].pop()
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
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected
