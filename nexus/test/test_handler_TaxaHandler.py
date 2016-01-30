"""Tests for TaxaHandler"""
import os
import unittest
from nexus import NexusReader, NexusFormatException

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')

class Test_TaxaHandler_AlternateNexusFormat(unittest.TestCase):
    expected = ['John', 'Paul', 'George', 'Ringo']
    
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))

    def test_block_find(self):
        assert 'taxa' in self.nex.blocks

    def test_taxa(self):
        for taxon in self.expected:
            assert taxon in self.nex.data.matrix
            assert taxon in self.nex.blocks['taxa'].taxa
        assert self.nex.blocks['taxa'].ntaxa == len(self.expected)
        
    def test_iterable(self):
        for idx, taxa in enumerate(self.nex.blocks['taxa']):
            assert taxa == self.expected[idx]
    
    def test_repr(self):
        assert repr(self.nex.blocks['taxa']) == "<NexusTaxaBlock: 4 taxa>"

    def test_error_on_incorrect_dimensions(self):
        with self.assertRaises(NexusFormatException):
            NexusReader().read_string("""
            #NEXUS
        
            begin taxa;
              dimensions ntax=2;
              taxlabels A B C;
            end;
            """)
        

if __name__ == '__main__':
    unittest.main()
