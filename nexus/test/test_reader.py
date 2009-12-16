"""Tests for nexus reading"""
from nexus import NexusReader
import os

EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'examples')

class Test_NexusReader_Core:
    """Test the Core functionality of NexusReader"""
    def test_read_file(self):
        nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert 'data' in nex.blocks
        assert 'Simon' in nex.blocks['data'].matrix
        
    def test_read_string(self):
        handle = open(os.path.join(EXAMPLE_DIR, 'example.nex'))
        data = handle.read()
        handle.close()
        nex = NexusReader()
        nex.read_string(data)
        assert 'data' in nex.blocks
        assert 'Simon' in nex.blocks['data'].matrix
    
    
class Test_DataHandler_SimpleNexusFormat:
    expected = {
        'Harry': '00',
        'Simon': '01',
        'Betty': '10',
        'Louise': '11',
    }
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        
    def test_block_find(self):
        assert 'data' in self.nex.blocks
        
    def test_format_string(self):
        # did we get the expected tokens in the format string?
        expected = {'datatype': 'standard', 'gap': '-', 'symbols': '01'}
        for k, v in expected.iteritems():
            assert self.nex.blocks['data'].format[k] == v, \
                "%s should equal %s and not %s" % (k, v, self.nex.blocks['data'].format[k])
        # did we get the right number of tokens?
        assert len(self.nex.blocks['data'].format) == len(expected)
        
    def test_taxa(self):
        # did we get the right taxa in the matrix?
        for taxon in self.expected:
            assert taxon in self.nex.blocks['data'].matrix
        # did we get the right number of taxa in the matrix?
        assert self.nex.blocks['data'].ntaxa == len(self.expected) == len(self.nex.blocks['data'].taxa)
        
    def test_characters(self):
        # did we parse the characters properly? 
        assert self.nex.blocks['data'].nchar == 2
        assert self.nex.blocks['data'].matrix['Harry'] == ['00']
        assert self.nex.blocks['data'].matrix['Simon'] == ['01']
        assert self.nex.blocks['data'].matrix['Betty'] == ['10']
        assert self.nex.blocks['data'].matrix['Louise'] == ['11']

    def test_iterable(self):
        for taxon, block in self.nex.blocks['data']:
            assert block[0] == self.expected[taxon]
            
        

class Test_DataHandler_AlternateNexusFormat:
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        
    def test_block_find(self):
        assert 'data' in self.nex.blocks
        
    def test_ntaxa_recovery(self):
        # the alternate format has a distinct taxa and characters block, and
        # we need to estimate the number of taxa in a different way.
        assert self.nex.blocks['data'].ntaxa == 4
        
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
        assert self.nex.blocks['data'].format is not None
        # did we get the expected tokens?
        for k, v in expected.iteritems():
            assert self.nex.blocks['data'].format[k] == v, \
                "%s should equal %s and not %s" % (k, v, self.nex.blocks['data'].format[k])
        # did we get the right number of tokens?
        assert len(self.nex.blocks['data'].format) == len(expected)
        
    def test_taxa(self):
        expected = ['John', 'Paul', 'George', 'Ringo']
        # did we get the taxa right?
        for e in expected:
            assert e in self.nex.blocks['data'].taxa, "%s should be in taxa" % e
        # did we get the number of taxa right?
        assert self.nex.blocks['data'].ntaxa == len(expected) == len(self.nex.blocks['data'].taxa)
    
    def test_data(self):
        # did we get the right amount of data?
        assert self.nex.blocks['data'].nchar == 4
        # are all the characters parsed correctly?
        for k in self.nex.blocks['data'].matrix:
            assert self.nex.blocks['data'].matrix[k] == ['actg']


class Test_TaxaHandler_AlternateNexusFormat:
    expected = ['John', 'Paul', 'George', 'Ringo']
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
    
    def test_block_find(self):
        assert 'taxa' in self.nex.blocks
    
    def test_taxa(self):
        for taxon in self.expected:
            assert taxon in self.nex.blocks['data'].matrix
            assert taxon in self.nex.blocks['taxa'].taxa
        assert self.nex.blocks['taxa'].ntaxa == len(self.expected)
    
    def test_iterable(self):
        for idx, taxa in enumerate(self.nex.blocks['taxa']):
            assert taxa == self.expected[idx]



class Test_TreeHandler_SimpleTreefile:
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
    
    def test_block_find(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks
        
    def test_treecount(self):
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 3 == self.nex.blocks['trees'].ntrees
        
    def test_iterable(self):
        for tree in self.nex.blocks['trees']:
            pass


def test_regression_whitespace_in_matrix():
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
        
    