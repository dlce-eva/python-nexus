"""Tests for nexus reading -- Maddison et al example"""
import os
import unittest
from nexus import NexusReader

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')

class Test_Maddison_et_al_Spec(unittest.TestCase):
    expected = {
        'fish': [_ for _ in 'ACATAGAGGGTACCTCTAAG'],
        'frog': [_ for _ in 'ACTTAGAGGCTACCTCTACG'],
        'snake': [_ for _ in 'ACTCACTGGGTACCTTTGCG'],
        'mouse': [_ for _ in 'ACTCAGACGGTACCTTTGCG'],
    }
    
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'maddison_et_al.nex'))
    
    def test_taxa(self):
        assert 'taxa' in self.nex.blocks
        for taxon in self.expected:
            assert taxon in self.nex.blocks['taxa'].taxa
        assert self.nex.blocks['taxa'].ntaxa == len(self.expected)
    
    def test_characters(self):
        assert 'characters' in self.nex.blocks
        assert self.nex.blocks['characters'].nchar == 20
        assert self.nex.blocks['characters'].ntaxa == 4
        assert self.nex.blocks['characters'].format['datatype'] == 'dna'
        for taxon in self.expected:
            assert taxon in self.nex.blocks['characters'].matrix
            assert self.nex.blocks['characters'].matrix[taxon] == self.expected[taxon]
    
    def test_data(self):  # characters is linked to `data`
        assert self.nex.blocks['data'] == self.nex.blocks['characters']
    
    def test_trees(self):
        assert 'trees' in self.nex.blocks
        assert self.nex.blocks['trees'].ntrees == 1
