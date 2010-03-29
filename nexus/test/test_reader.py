"""Tests for nexus reading"""
import os
import re
from nexus import NexusReader
from nexus.reader import GenericHandler, DataHandler, TreeHandler

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
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE)

    def test__load_characters(self):
        for site, data in self.nex.data.characters.items():
            for taxon, value in data.items():
                assert value == self.expected[taxon][site]

    def test_get_site(self):
        for i in (0, 1):
            site_data = self.nex.data.characters[i]
            for taxon, value in site_data.items():
                assert self.expected[taxon][i] == value

    def test_numcharacters_checking(self):
        nex = NexusReader()
        nex.read_string(
            """Begin data;
            Dimensions ntax=1 nchar=2;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              1
            ;""")
        assert nex.data.nchar == 1
        
        nex = NexusReader()
        nex.read_string(
            """Begin data;
            Dimensions ntax=4 nchar=1;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              11111
            ;""")
        assert nex.data.nchar == 5


            

class Test_DataHandler_InterleavedNexusFormat:
    def test_interleave_matrix_parsing(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example3.nex'))
        assert nexus.data.ntaxa == 2 == len(nexus.data.taxa)
        assert nexus.data.nchar == 6
        for taxon, blocks in nexus.data:
            for i in range(0, nexus.data.nchar):
                assert blocks[i] == str(i)
    
    

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


class Test_DataHandler_CharacterBlockNexusFormat:
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example-characters.nex'))
        
    def test_block_find(self):
        assert 'data' in self.nex.blocks
    
    def test_charblock_find(self):
        assert hasattr(self.nex.data, 'characters')
    
    def test_taxa(self):
        assert self.nex.data.ntaxa == 5
        
    def test_data(self):
        assert self.nex.data.nchar == 5
        
    def test_charlabels(self):
         assert self.nex.data.charlabels[0] == 'CHAR_A'
         assert self.nex.data.charlabels[1] == 'CHAR_B'
         assert self.nex.data.charlabels[2] == 'CHAR_C'
         assert self.nex.data.charlabels[3] == 'CHAR_D'
         assert self.nex.data.charlabels[4] == 'CHAR_E'
        
    def test_label_parsing(self):
        assert 'CHAR_A' in self.nex.data.characters
        assert 'CHAR_B' in self.nex.data.characters
        assert 'CHAR_C' in self.nex.data.characters
        assert 'CHAR_D' in self.nex.data.characters
        assert 'CHAR_E' in self.nex.data.characters
        
    def test_matrix(self):
        for taxon in ("A", "B", "C", "D", "E"):
            for index, expected_value in enumerate(("A", "B", "C", "D", "E")):
                assert self.nex.data.matrix[taxon][index] == expected_value
            
    def test_characters(self):
        for site in ("A", "B", "C", "D", "E"):
            # All sites in CHAR_A are state "A", and all in CHAR_B and "B" etc
            for taxon in ("A", "B", "C", "D", "E"):
                assert self.nex.data.characters["CHAR_%s" % site][taxon] == site


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
    

class Test_TreeHandler_TranslatedTreefile:
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example-translated.trees'))
    
    def test_block_find(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks
    
    def test_treecount(self):
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 3 == self.nex.blocks['trees'].ntrees
        assert len(self.nex.trees.trees) == 3 == self.nex.trees.ntrees
    
    def test_iterable(self):
        for tree in self.nex.blocks['trees']:
            tree # will raise something if unable to iterate
        for tree in self.nex.trees:
            tree
    
    def test_was_translated_flag_set(self):
        assert self.nex.trees.was_translated == True
        
    def test_parsing_sets_translators(self):
        assert len(self.nex.trees.translators) == 13 # 13 taxa in example trees
        
    def test_been_detranslated_flag_set(self):
        assert self.nex.trees._been_detranslated == False
        self.nex.trees.detranslate()
        assert self.nex.trees._been_detranslated == True

    def test_write(self):
        assert self.nex.trees._been_detranslated == False
        written = self.nex.trees.write()
        expected = open(os.path.join(EXAMPLE_DIR, 'example-translated.trees'), 'rU').read()
        # remove leading header which isn't generated by .write()
        expected = expected.lstrip("#NEXUS\n\n")
        # remove tabs since we reformat things a bit
        expected = expected.replace("\t", "").strip()
        written = written.replace("\t", "").strip()
        assert expected == written, "%s\n----\n%s" % (expected, written)
    
    def test_no_error_on_multiple_translate(self):
        assert self.nex.trees._been_detranslated == False
        self.nex.trees.detranslate()
        assert self.nex.trees._been_detranslated == True
        self.nex.trees.detranslate() # should not cause an error

    def test_detranslate(self):
        assert self.nex.trees._been_detranslated == False
        self.nex.trees.detranslate()
        # should NOW be the same as tree 0 in example.trees
        other_tree_file = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
        assert other_tree_file.trees[0] == self.nex.trees[0]
    

class Test_TreeHandler_BEAST_Format:

    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example_beast.trees'))

    def test_read_BEAST_format(self):
        assert self.nex.trees[0].startswith('tree STATE_201000')

    def test_block_find(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks

    def test_treecount(self):
        assert len(self.nex.blocks['trees'].trees) == 1 == self.nex.blocks['trees'].ntrees
        assert len(self.nex.trees.trees) == 1 == self.nex.trees.ntrees

    def test_flag_set(self):
        assert self.nex.trees.was_translated == True

    def test_parsing_sets_translators(self):
        assert len(self.nex.trees.translators) == 38 # 38 taxa in example trees

    # def test_detranslate_BEAST_format_extended(self):
    #     print self.nex.trees[0]
    #     self.nex.trees.detranslate()
    #     print self.nex.trees[0]
    #     for index, taxon in self.nex.trees.translators.items():
    #         # check if the taxon name is present in the tree...
    #         assert taxon in self.nex.trees[0], "Expecting taxon %s in tree description" % taxon
    #     assert self.nex.trees._been_detranslated == True
    

class Test_TreeHandler__detranslate_tree:
    
    def test_no_change(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((Chris,Bruce),Tom);"
        newtree = "tree a = ((Chris,Bruce),Tom);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree,  "Unable to correctly NOT translate a simple tree"
        
    def test_no_change_branchlengths(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
        newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree, "Unable to correctly NOT translate a tree with branchlengths"
    
    def test_change(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((0,1),2);"
        newtree = "tree a = ((Chris,Bruce),Tom);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree,  "Unable to correctly detranslate a simple tree"
    
    def test_change_branchlengths(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((0:0.1,1:0.2):0.3,2:0.4);"
        newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree,  "Unable to correctly detranslate a tree with branchlengths"

    def test_BEAST_format(self):
        translatetable = {'1': 'Chris', '2': 'Bruce', '3': 'Tom'}
        oldtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((1:[&rate=1.0]48.056,3:[&rate=1.0]48.056):[&rate=1.0]161.121,2:[&rate=1.0]209.177);"
        newtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((Chris:[&rate=1.0]48.056,Tom:[&rate=1.0]48.056):[&rate=1.0]161.121,Bruce:[&rate=1.0]209.177);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable) 
        assert trans == newtree, "Unable to correctly detranslate a BEAST tree"



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
        
    

def test_badchars_quoted_in_taxaname():
    nex = NexusReader()
    nex.read_string("""
    #NEXUS

    Begin trees;
    	Translate
    		1 MANGIC_Bugan,
    		2 MANGIC_Paliu,
    		3 MANGIC_Mang,
    		4 PALAUNGWA_Danaw,
    		5 'PALAUNGWA_De.Ang'
        ;
        tree 1 = (1,2,3,4,5);
    """)
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
    