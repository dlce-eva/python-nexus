"""Tests for nexus reading"""
from nexus import NexusReader
import os

EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'examples')

class Test_NexusReader_Core:
    """Test the Core functionality of NexusReader"""
    def test_read_file(self):
        nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert 'data' in nex.blocks.keys()
        assert 'Simon' in nex.blocks['data'].matrix.keys()
        
    def test_read_string(self):
        handle = open(os.path.join(EXAMPLE_DIR, 'example.nex'))
        data = handle.read()
        handle.close()
        nex = NexusReader()
        nex.read_string(data)
        assert 'data' in nex.blocks.keys()
        assert 'Simon' in nex.blocks['data'].matrix.keys()
    
    
class Test_DataHandler_SimpleStandardNexus:
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        
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
        assert self.nex.blocks['data'].matrix['Harry'] == ['00']
        assert self.nex.blocks['data'].matrix['Simon'] == ['01']
        assert self.nex.blocks['data'].matrix['Betty'] == ['10']
        assert self.nex.blocks['data'].matrix['Louise'] == ['11']


class Test_TreeHandler_SimpleTreefile:
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
    
    def test_block_find(self):
        assert 'trees' in self.nex.blocks
        
    def test_treecount(self):
        assert len(self.nex.blocks['trees'].trees) == 3 == self.nex.blocks['trees'].ntrees
    


def test_whitespace_in_matrix_regression():
    """Regression: Test that leading whitespace in a data matrix is parsed ok"""
    nex = NexusReader()
    nex.read_string("""
    #NEXUS 
    
    Begin data;
        Dimensions ntax=4 nchar=2;
                            Format datatype=standard symbols="01" gap=-;
            Matrix
    Harry              00
            Simon              01
                    Betty              10
                                Louise 11
        ;
    End;
    """)
    assert nex.blocks['data'].nchar == 2
    assert nex.blocks['data'].matrix['Harry'] == ['00']
    assert nex.blocks['data'].matrix['Simon'] == ['01']
    assert nex.blocks['data'].matrix['Betty'] == ['10']
    assert nex.blocks['data'].matrix['Louise'] == ['11']
        
    