"""Regression Tests"""
import os
import re
import unittest
from nexus import NexusReader
from nexus.reader import GenericHandler, DataHandler, TreeHandler

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')
REGRESSION_DIR = os.path.join(os.path.dirname(__file__), 'regression')


class Test_DataHandler_Regression_WhitespaceInMatrix(unittest.TestCase):
    """Regression: Test that leading whitespace in a data matrix is parsed ok"""
    def test_regression(self):
        nex = NexusReader(os.path.join(REGRESSION_DIR, 'white_space_in_matrix.nex'))
        assert nex.blocks['data'].nchar == 2
        assert nex.blocks['data'].matrix['Harry'] == ['0', '0']
        assert nex.blocks['data'].matrix['Simon'] == ['0', '1']
        assert nex.blocks['data'].matrix['Betty'] == ['1', '0']
        assert nex.blocks['data'].matrix['Louise'] == ['1', '1']
        
    

class Test_TreeHandler_Regression_RandomAPETrees(unittest.TestCase):
    """Regression: Test that we can parse randomly generated APE/R trees"""
    def test_regression(self):
        nex = NexusReader(os.path.join(REGRESSION_DIR, 'ape_random.trees'))
        assert nex.trees.ntrees == 2


class Test_TreeHandler_Regression_BadCharsInTaxaName(unittest.TestCase):
    def test_regression(self):
        nex = NexusReader(os.path.join(REGRESSION_DIR, 'bad_chars_in_taxaname.trees'))
        # did we get a tree block?
        assert 'trees' in nex.blocks
        # did we find 3 trees?
        assert len(nex.blocks['trees'].trees) == 1 == nex.blocks['trees'].ntrees
        # did we get the translation parsed properly.
        assert nex.trees.was_translated == True
        assert len(nex.trees.translators) == 5 # 5 taxa in example trees
        # check last entry
        assert nex.trees.translators['5'] == 'PALAUNGWA_De.Ang'
        # check detranslate
        nex.trees.detranslate()
        assert '(MANGIC_Bugan,MANGIC_Paliu,MANGIC_Mang,PALAUNGWA_Danaw,PALAUNGWA_De.Ang)' in nex.trees[0]


class Test_TaxaHandler_Regression_Mesquite(unittest.TestCase):
    """Regression: Test that we can parse MESQUITE taxa blocks"""
    def setUp(self):
        self.nex = NexusReader(os.path.join(REGRESSION_DIR, 'mesquite_taxa_block.nex'))
        
    def test_taxa_block(self):
        for taxon in ['A', 'B', 'C']:
            assert taxon in self.nex.taxa
        # did we get the right number of taxa in the matrix?
        assert self.nex.taxa.ntaxa == len(self.nex.taxa.taxa) == 3
        
    def test_taxa_block_attributes(self):
        assert 'taxa' in self.nex.blocks
        assert len(self.nex.taxa.attributes) == 1
        assert 'TITLE Untitled_Block_of_Taxa;' in self.nex.taxa.attributes
        

class Test_TreeHandler_Regression_Mesquite(unittest.TestCase):
    """Regression: Test that we can parse MESQUITE taxa blocks"""
    def setUp(self):
        self.nex = NexusReader(os.path.join(REGRESSION_DIR, 'mesquite_formatted_branches.trees'))
    
    def test_found_trees(self):
        assert self.nex.trees.ntrees == 1
    
    def test_found_taxa(self):
        assert len(self.nex.trees.taxa) == 3
        assert 'A' in self.nex.trees.taxa
        assert 'B' in self.nex.trees.taxa
        assert 'C' in self.nex.trees.taxa
        
    def test_was_translated(self):
        assert self.nex.trees.was_translated == True
    
    def test_translation(self):
        assert self.nex.trees.translators['1'] == 'A'
        assert self.nex.trees.translators['2'] == 'B'
        assert self.nex.trees.translators['3'] == 'C'
        
        