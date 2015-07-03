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
            '^begin data;$',
            '^\s+dimensions ntax=5 nchar=2;$',
            '^\s+format datatype=standard gap=- symbols="012";$',
            '^matrix$',
            '^Simon\s+01$',
            '^Louise\s+11$',
            '^Betty\s+10$',
            '^Harry\s+00$',
            '^Elvis\s+12$',
            '^\s+;$',
            '^end;$',
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
            '^begin data;$',
            '^\s+dimensions ntax=3 nchar=2;$',
            '^\s+format datatype=standard gap=- symbols="01";$',
            '^matrix$',
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

        # should NOT be here
        assert re.search('^Simon\s+01$', written, re.MULTILINE) is None, \
            'Expected Taxon "Simon" to be Deleted'

    def test_add_character(self):
        assert self.nex.data.nchar == 2
        for taxon in self.nex.data.matrix:
            self.nex.data.matrix[taxon].append('9')
        expected_patterns = [
            '^begin data;$',
            '^\s+dimensions ntax=4 nchar=3;$',
            '^\s+format datatype=standard gap=- symbols="019";$',
            '^matrix$',
            '^Simon\s+019$',
            '^Louise\s+119$',
            '^Betty\s+109$',
            '^Harry\s+009$',
            '^\s+;$',
            '^end;$',
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
            '^begin data;$',
            '^\s+dimensions ntax=4 nchar=1;$',
            '^\s+format datatype=standard gap=- symbols="01";$',
            '^matrix$',
            '^Simon\s+0$',
            '^Louise\s+1$',
            '^Betty\s+1$',
            '^Harry\s+0$',
            '^\s+;$',
            '^end;$',
        ]
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected

if __name__ == '__main__':
    unittest.main()
