"""Tests for TaxaHandler"""
import os
import unittest
from nexus.reader import NexusReader
from nexus.exceptions import NexusFormatException

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
    
    def test_wrap_label_in_quotes_only_when_needed(self):
        self.nex.taxa.taxa[0] = "long name"
        output = self.nex.taxa.write()
        assert "[1] 'long name'" in output
        assert "[2] Paul" in output
        assert "[3] George" in output
        assert "[4] Ringo" in output
        
    def test_error_on_incorrect_dimensions(self):
        with self.assertRaises(NexusFormatException):
            NexusReader().read_string("""
            #NEXUS
        
            begin taxa;
              dimensions ntax=2;
              taxlabels A B C;
            end;
            """)
    
    def test_annotation_read(self):
        nex = NexusReader().read_string("""
        #NEXUS
        BEGIN TAXA;
            DIMENSIONS  NTAX=3;
            TAXLABELS
            A[&!color=#aaaaaa]
            B[&!color=#bbbbbb]
            C[&!color=#cccccc]
        END;
        """)
        nex.taxa.annotations['A'] = '[&!color=#aaaaaa]'
        nex.taxa.annotations['B'] = '[&!color=#bbbbbb]'
        nex.taxa.annotations['C'] = '[&!color=#cccccc]'
        
        out = nex.taxa.write()
        assert 'A[&!color=#aaaaaa]' in out
        assert 'B[&!color=#bbbbbb]' in out
        assert 'C[&!color=#cccccc]' in out
        
    def test_annotation_write(self):
        self.nex.taxa.annotations['John'] = '[&!color=#006fa6]'
        assert 'John[&!color=#006fa6]' in self.nex.taxa.write()
