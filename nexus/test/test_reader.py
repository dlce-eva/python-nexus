"""Tests for nexus reading"""
import os
import re
from nexus import NexusReader
from nexus.reader import DataHandler, GenericHandler

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
    
    def test_generic_readwrite(self):
        expected = """Begin data;
        Dimensions ntax=4 nchar=2;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              00
        Simon              01
        Betty              10
        Louise             11
        ;
        """.split("\n")
        nex = NexusReader()
        nex.handlers['data'] = GenericHandler
        nex.read_file(os.path.join(EXAMPLE_DIR, 'example.nex'))
        for line in nex.data.write().split("\n"):
            e = expected.pop(0).strip()
            assert line.strip() == e
        
    def test_write(self):
        nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
        text = open(os.path.join(EXAMPLE_DIR, 'example.trees')).read()
        assert text == nex.write()
    
class Test_DataHandler_SimpleNexusFormat:
    expected = {
        'Harry': ['0', '0'],
        'Simon': ['0', '1'],
        'Betty': ['1', '0'],
        'Louise': ['1', '1'],
    }
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        
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
                "%s should equal %s and not %s" % (k, v, self.nex.data.format[k])
        # did we get the right number of tokens?
        assert len(self.nex.data.format) == len(expected)
        
    def test_taxa(self):
        # did we get the right taxa in the matrix?
        for taxon in self.expected:
            assert taxon in self.nex.data.matrix
        # did we get the right number of taxa in the matrix?
        assert self.nex.data.ntaxa == len(self.expected) == len(self.nex.data.taxa)
        
    def test_characters(self):
        # did we parse the characters properly? 
        assert self.nex.data.nchar == 2
        for taxon, expected in self.expected.items():
            assert self.nex.data.matrix[taxon] == expected

    def test_iterable(self):
        for taxon, block in self.nex.data:
            assert block == self.expected[taxon]
            
    def test_parse_format_line(self):
        d = DataHandler()
        f = d.parse_format_line('Format datatype=standard symbols="01" gap=-;')
        assert f['datatype'] == 'standard', "Expected 'standard', but got '%s'" % f['datatype']
        assert f['symbols'] == '01', "Expected '01', but got '%s'" % f['symbols']
        assert f['gap'] == '-', "Expected 'gap', but got '%s'" % f['gap']
        
        f = d.parse_format_line('FORMAT datatype=RNA missing=? gap=- symbols="ACGU" labels interleave;')
        assert f['datatype'] == 'rna', "Expected 'rna', but got '%s'" % f['datatype']
        assert f['missing'] == '?', "Expected '?', but got '%s'" % f['missing']
        assert f['gap'] == '-', "Expected '-', but got '%s'" % f['gap']
        assert f['symbols'] == 'acgu', "Expected 'acgu', but got '%s'" % f['symbols']
        assert f['labels'] == True, "Expected <True>, but got '%s'" % f['labels']
        assert f['interleave'] == True, "Expected <True>, but got '%s'" % f['interleave']
    
    def test_write(self):
        expected_patterns = [
            '^begin data;$',
            '^\s+dimensions ntax=4 nchar=2;$',
            '^\s+format datatype=standard symbols="01" gap=-;$',
            '^matrix$',
            '^Simon\s+01$',
            '^Louise\s+11$',
            '^Betty\s+10$',
            '^Harry\s+00$',
            '^\s+;$',
            '^end;$',
        ]
        written = self.nex.write()
        print written
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE)


class Test_DataHandler_AlternateNexusFormat:
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
                "%s should equal %s and not %s" % (k, v, self.nex.data.format[k])
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

    def test_write(self):
        ###print self.nex.write()
        raise NotImplemented, "Not yet implemented."


class Test_TaxaHandler_AlternateNexusFormat:
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
    

class Test_TreeHandler_SimpleTreefile:
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
    
    def test_block_find(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks
        
    def test_treecount(self):
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 3 == self.nex.blocks['trees'].ntrees
        assert len(self.nex.trees.trees) == 3 == self.nex.trees.ntrees
        
    def test_iterable(self):
        for tree in self.nex.blocks['trees']:
            pass
        for tree in self.nex.trees:
            pass
            
    def test_write(self):
        written = self.nex.trees.write()
        expected = open(os.path.join(EXAMPLE_DIR, 'example.trees'), 'rU').read()
        # remove leading header which isn't generated by .write()
        expected = expected.lstrip("#NEXUS\n\n") 
        assert expected == written


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
    assert nex.blocks['data'].matrix['Harry'] == ['0', '0']
    assert nex.blocks['data'].matrix['Simon'] == ['0', '1']
    assert nex.blocks['data'].matrix['Betty'] == ['1', '0']
    assert nex.blocks['data'].matrix['Louise'] == ['1', '1']
        
    