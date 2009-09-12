"""Tests for nexus reading"""
import nose
from reader import Nexus

class Test_DataHandler_SimpleStandardNexus:
    def setup(self):
        self.nex = Nexus('examples/example.nex')
        
    def test_block_find(self):
        assert 'data' in self.nex.blocks.keys()
        
    def test_format_string(self):
        assert self.nex.blocks['data'].format['datatype'] == 'standard'
        assert self.nex.blocks['data'].format['gap'] == '-'
        assert self.nex.blocks['data'].format['symbols'] == '01'
        
    def test_taxa(self):
        assert 'Simon' in self.nex.blocks['data'].matrix.keys()
        assert 'Harry' in self.nex.blocks['data'].matrix.keys()
        assert 'Betty' in self.nex.blocks['data'].matrix.keys()
        assert 'Louise' in self.nex.blocks['data'].matrix.keys()
        assert self.nex.blocks['data'].taxa == ['Harry', 'Simon', 'Betty', 'Louise']
        assert self.nex.blocks['data'].ntaxa == 4 == len(self.nex.blocks['data'].taxa)
        
    def test_characters(self):
        assert self.nex.blocks['data'].nchar == 2
        print self.nex.blocks['data'].matrix
        assert self.nex.blocks['data'].matrix['Harry'] == ['00']
        assert self.nex.blocks['data'].matrix['Simon'] == ['01']
        assert self.nex.blocks['data'].matrix['Betty'] == ['10']
        assert self.nex.blocks['data'].matrix['Louise'] == ['11']


class Test_TreeHandler_SimpleTreefile:
    def setup(self):
        self.nex = Nexus('examples/example.trees')
    
    def test_block_find(self):
        assert 'trees' in self.nex.blocks
        
    def test_treecount(self):
        assert len(self.nex.blocks['trees'].trees) == 3 == self.nex.blocks['trees'].ntrees
        