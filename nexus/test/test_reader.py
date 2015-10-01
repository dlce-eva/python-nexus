"""Tests for nexus reading"""
import os
import re
import warnings
import unittest
from nexus import NexusReader
from nexus.reader import GenericHandler, DataHandler, TreeHandler

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')

#warnings.simplefilter("always")

class Test_NexusReader_Core(unittest.TestCase):
    """Test the Core functionality of NexusReader"""
    def test_read_file(self):
        nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert 'data' in nex.blocks
        assert 'Simon' in nex.blocks['data'].matrix

    def test_read_gzip_file(self):
        # first, MAKE a gzip file
        import gzip
        from tempfile import NamedTemporaryFile
        tmp = NamedTemporaryFile(delete=False, suffix=".gz")
        tmp.close()
        with open(os.path.join(EXAMPLE_DIR, 'example.nex'), 'rb') as h:
            content = h.read()
        
        with gzip.open(tmp.name, 'wb') as h:
            h.write(content)
        
        # test it's ok
        nex = NexusReader(tmp.name)
        assert 'data' in nex.blocks
        assert 'Simon' in nex.blocks['data'].matrix
        os.unlink(tmp.name)        # cleanup

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


class Test_DataHandler_parse_sites(unittest.TestCase):
    def test_simple(self):
        assert DataHandler()._parse_sites('123') == ['1', '2', '3']

    def test_multi(self):
        assert DataHandler()._parse_sites('1(12)') == ['1', '12']

    def test_comma(self):
        assert DataHandler()._parse_sites('123(4,5)56') == \
            ['1', '2', '3', '4,5', '5', '6']

    def test_space(self):
        assert DataHandler()._parse_sites('123(4 5)56') == \
            ['1', '2', '3', '4 5', '5', '6']

    def test_sequence(self):
        assert DataHandler()._parse_sites("ACGTU?") == \
            ['A', 'C', 'G', 'T', 'U', '?']


class Test_DataHandler_SimpleNexusFormat(unittest.TestCase):
    expected = {
        'Harry': ['0', '0'],
        'Simon': ['0', '1'],
        'Betty': ['1', '0'],
        'Louise': ['1', '1'],
    }

    def setUp(self):
        self.nex = NexusReader(
            os.path.join(EXAMPLE_DIR, 'example.nex')
        )

    def test_block_find(self):
        assert 'data' in self.nex.blocks
        assert hasattr(self.nex, 'data')
        assert self.nex.data == self.nex.data

    def test_raw(self):
        print(self.nex.data.block)
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
                "%s should equal %s and not %s" % \
                (k, v, self.nex.data.format[k])
        # did we get the right number of tokens?
        assert len(self.nex.data.format) == len(expected)

    def test_taxa(self):
        # did we get the right taxa in the matrix?
        for taxon in self.expected:
            assert taxon in self.nex.data.matrix
        # did we get the right number of taxa in the matrix?
        assert self.nex.data.ntaxa == len(self.expected)
        assert self.nex.data.ntaxa == len(self.nex.data.taxa)

    def test_matrix(self):
        assert self.nex.data.nchar == 2
        for taxon, expected in self.expected.items():
            assert self.nex.data.matrix[taxon] == expected
            
    def test_characters(self):
        for site, data in self.nex.data.characters.items():
            for taxon, value in data.items():
                assert value == self.expected[taxon][site]
                
    def test_iterable(self):
        for taxon, block in self.nex.data:
            assert block == self.expected[taxon]

    def test_parse_format_line(self):
        d = DataHandler()
        f = d.parse_format_line('Format datatype=standard gap=- symbols="01";')
        assert f['datatype'] == 'standard', \
            "Expected 'standard', but got '%s'" % f['datatype']
        assert f['symbols'] == '01', \
            "Expected '01', but got '%s'" % f['symbols']
        assert f['gap'] == '-', \
            "Expected 'gap', but got '%s'" % f['gap']
        
        fmt = 'FORMAT datatype=RNA missing=? symbols="ACGU" labels interleave;'
        f = d.parse_format_line(fmt)
        assert f['datatype'] == 'rna', \
            "Expected 'rna', but got '%s'" % f['datatype']
        assert f['missing'] == '?', \
            "Expected '?', but got '%s'" % f['missing']
        assert f['symbols'] == 'acgu', \
            "Expected 'acgu', but got '%s'" % f['symbols']
        assert f['labels'] is True, \
            "Expected <True>, but got '%s'" % f['labels']
        assert f['interleave'] is True, \
            "Expected <True>, but got '%s'" % f['interleave']

    def test_write(self):
        expected_patterns = [
            '^begin data;$',
            '^\s+dimensions ntax=4 nchar=2;$',
            '^\s+format datatype=standard gap=- symbols="01";$',
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
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected

    def test_get_site(self):
        for i in (0, 1):
            site_data = self.nex.data.characters[i]
            for taxon, value in site_data.items():
                assert self.expected[taxon][i] == value

    def test_incorrect_dimensions_warnings_ntaxa(self):
        nex = NexusReader()
        with warnings.catch_warnings(record=True) as w:
            nex.read_string(
                """Begin data;
                Dimensions ntax=5 nchar=1;
                Format datatype=standard symbols="01" gap=-;
                Matrix
                Harry              1
                ;""")
            assert len(w) == 1, 'Expected 1 warning, got %r' % w
            assert issubclass(w[-1].category, UserWarning)
            assert "Expected" in str(w[-1].message)
            assert nex.data.nchar == 1

    def test_incorrect_dimensions_warnings_nchar(self):
        with warnings.catch_warnings(record=True) as w:
            nex = NexusReader()
            nex.read_string(
                """Begin data;
                Dimensions ntax=1 nchar=5;
                Format datatype=standard symbols="01" gap=-;
                Matrix
                Harry              1
                ;""")
            assert len(w) == 1, 'Expected 1 warning, got %r' % w
            assert issubclass(w[-1].category, UserWarning)
            assert "Expected" in str(w[-1].message)
            assert nex.data.nchar == 1


class Test_DataHandler_InterleavedNexusFormat(unittest.TestCase):
    def test_interleave_matrix_parsing(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example3.nex'))
        assert nexus.data.ntaxa == 2 == len(nexus.data.taxa)
        assert nexus.data.nchar == 6
        for taxon, blocks in nexus.data:
            for i in range(0, nexus.data.nchar):
                assert blocks[i] == str(i)



class Test_DataHandler_AlternateNexusFormat(unittest.TestCase):
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
                "%s should equal %s and not %s" % \
                (k, v, self.nex.data.format[k])
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


class Test_DataHandler_CharacterBlockNexusFormat(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(EXAMPLE_DIR, 'example-characters.nex')
        )

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
            for t in ("A", "B", "C", "D", "E"):
                assert self.nex.data.characters["CHAR_%s" % site][t] == site


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


class Test_TreeHandler_SimpleTreefile(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))

    def test_block_find(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks

    def test_treecount(self):
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 3
        assert self.nex.blocks['trees'].ntrees == 3
        assert len(self.nex.trees.trees) == 3
        assert self.nex.trees.ntrees == 3

    def test_taxa(self):
        expected = [
            'Chris', 'Bruce', 'Tom', 'Henry', 'Timothy', 'Mark', 'Simon',
            'Fred', 'Kevin', 'Roger', 'Michael', 'Andrew', 'David'
        ]
        assert len(self.nex.trees.taxa) == len(expected)
        for taxon in expected:
            assert taxon in self.nex.trees.taxa

    def test_iterable(self):
        for tree in self.nex.blocks['trees']:
            pass
        for tree in self.nex.trees:
            pass

    def test_write(self):
        written = self.nex.trees.write()
        expected = open(
            os.path.join(EXAMPLE_DIR, 'example.trees'), 'rU'
        ).read()
        # remove leading header which isn't generated by .write()
        expected = expected.lstrip("#NEXUS\n\n")
        assert expected == written


class Test_TreeHandler_TranslatedTreefile(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(EXAMPLE_DIR, 'example-translated.trees')
        )

    def test_block_find(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks

    def test_treecount(self):
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 3
        assert self.nex.blocks['trees'].ntrees == 3
        assert len(self.nex.trees.trees) == 3
        assert self.nex.trees.ntrees == 3

    def test_iterable(self):
        for tree in self.nex.blocks['trees']:
            tree  # will raise something if unable to iterate
        for tree in self.nex.trees:
            tree

    def test_taxa(self):
        expected = [
            'Chris', 'Bruce', 'Tom', 'Henry', 'Timothy', 'Mark', 'Simon',
            'Fred', 'Kevin', 'Roger', 'Michael', 'Andrew', 'David'
        ]
        assert len(self.nex.trees.taxa) == len(expected)
        for taxon in expected:
            assert taxon in self.nex.trees.taxa

    def test_was_translated_flag_set(self):
        assert self.nex.trees.was_translated

    def test_parsing_sets_translators(self):
        assert len(self.nex.trees.translators) == 13

    def test_been_detranslated_flag_set(self):
        assert not self.nex.trees._been_detranslated
        self.nex.trees.detranslate()
        assert self.nex.trees._been_detranslated

    def test_write(self):
        assert not self.nex.trees._been_detranslated
        written = self.nex.trees.write()
        expected = open(
            os.path.join(EXAMPLE_DIR, 'example-translated.trees'), 'rU'
        ).read()
        # remove leading header which isn't generated by .write()
        expected = expected.lstrip("#NEXUS\n\n")
        # remove tabs since we reformat things a bit
        expected = expected.replace("\t", "").strip()
        written = written.replace("\t", "").strip()
        assert expected == written, "%s\n----\n%s" % (expected, written)

    def test_no_error_on_multiple_translate(self):
        assert not self.nex.trees._been_detranslated
        self.nex.trees.detranslate()
        assert self.nex.trees._been_detranslated
        self.nex.trees.detranslate()  # should not cause an error

    def test_detranslate(self):
        assert not self.nex.trees._been_detranslated
        self.nex.trees.detranslate()
        # should NOW be the same as tree 0 in example.trees
        other_tree_file = NexusReader(
            os.path.join(EXAMPLE_DIR, 'example.trees')
        )
        assert other_tree_file.trees[0] == self.nex.trees[0]



class Test_TreeHandler_BEAST_Format(unittest.TestCase):

    def setUp(self):
        self.nex = NexusReader(
            os.path.join(EXAMPLE_DIR, 'example-beast.trees')
        )

    def test_read_BEAST_format(self):
        assert self.nex.trees[0].startswith('tree STATE_201000')

    def test_block_find(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks

    def test_taxa(self):
        expected = [
            "R1", "B2", "S3", "T4", "A5", "E6", "U7", "T8", "T9", "F10", "U11",
            "T12", "N13", "F14", "K15", "N16", "I17", "L18", "S19", "T20",
            "V21", "R22", "M23", "H24", "M25", "M26", "M27", "R28", "T29",
            "M30", "P31", "T32", "R33", "P34", "R35", "W36", "F37", "F38"
        ]
        assert len(self.nex.trees.taxa) == len(expected)
        for taxon in expected:
            assert taxon in self.nex.trees.taxa

    def test_treecount(self):
        assert len(self.nex.blocks['trees'].trees) == 1
        assert self.nex.blocks['trees'].ntrees == 1
        assert len(self.nex.trees.trees) == 1
        assert self.nex.trees.ntrees == 1

    def test_flag_set(self):
        assert self.nex.trees.was_translated

    def test_parsing_sets_translators(self):
        assert len(self.nex.trees.translators) == 38

    def test_detranslate_BEAST_format_extended(self):
        self.nex.trees.detranslate()
        for index, taxon in self.nex.trees.translators.items():
            # check if the taxon name is present in the tree...
            assert taxon in self.nex.trees[0], \
                "Expecting taxon %s in tree description" % taxon
        assert self.nex.trees._been_detranslated


class Test_TreeHandler_translate_regex(unittest.TestCase):

    def setUp(self):
        th = TreeHandler()
        self.findall = th._findall_chunks

    def test_tree(self):
        expected = {
            0: {
                'start': '(',
                'taxon': 'Chris',
                'comment': None,
                'branch': None,
                'end': ','
            },
            1: {
                'start': ',',
                'taxon': 'Bruce',
                'comment': None,
                'branch': None,
                'end': ')'
            },
            2: {
                'start': ',',
                'taxon': 'Tom',
                'comment': None,
                'branch': None,
                'end': ')'
            },
        }
        found = self.findall("tree a = ((Chris,Bruce),Tom);")
        assert len(found) == 3
        for match in expected:
            for key in expected[match]:
                if expected[match][key] != found[match][key]:
                    raise AssertionError(
                        "Expected %s for %s, got %s" %
                        (expected[match][key], key, found[match][key])
                    )

    def test_tree_digits(self):
        expected = {
            0: {
                'start': '(',
                'taxon': '1',
                'comment': None,
                'branch': None,
                'end': ','
            },
            1: {
                'start': ',',
                'taxon': '2',
                'comment': None,
                'branch': None,
                'end': ')'
            },
            2: {
                'start': ',',
                'taxon': '3',
                'comment': None,
                'branch': None,
                'end': ')'
            },
        }
        found = self.findall("tree a = ((1,2),3);")
        assert len(found) == 3
        for match in expected:
            for key in expected[match]:
                if expected[match][key] != found[match][key]:
                    raise AssertionError(
                        "Expected %s for %s, got %s" %
                        (expected[match][key], key, found[match][key])
                    )

    def test_tree_with_branchlengths(self):
        expected = {
            0: {
                'start': '(',
                'taxon': '1',
                'comment': None,
                'branch': '0.1',
                'end': ','
            },
            1: {
                'start': ',',
                'taxon': '2',
                'comment': None,
                'branch': '0.2',
                'end': ')'
            },
            2: {
                'start': ',',
                'taxon': '3',
                'comment': None,
                'branch': '0.3',
                'end': ')'
            },
        }
        found = self.findall("tree a = ((1:0.1,2:0.2):0.9,3:0.3):0.9;")
        assert len(found) == 3
        for match in expected:
            for key in expected[match]:
                if expected[match][key] != found[match][key]:
                    raise AssertionError(
                        "Expected %s for %s, got %s" %
                        (expected[match][key], key, found[match][key])
                    )

    def test_tree_complex(self):
        expected = {
            0: {
                'start': '(',
                'taxon': '1',
                'comment': '[&var=1]',
                'branch': '0.1',
                'end': ','
            },
            1: {
                'start': ',',
                'taxon': '2',
                'comment': '[&var=2]',
                'branch': '0.2',
                'end': ')'
            },
            2: {
                'start': ',',
                'taxon': '3',
                'comment': '[&var=4]',
                'branch': '0.3',
                'end': ')'
            },
        }
        found = self.findall(
            "tree a = ((1:[&var=1]0.1,2:[&var=2]0.2):[&var=3]0.9,3:[&var=4]0.3):[&var=5]0.9;"
        )
        assert len(found) == 3
        for match in expected:
            for key in expected[match]:
                if expected[match][key] != found[match][key]:
                    raise AssertionError(
                        "Expected %s for %s, got %s" %
                        (expected[match][key], key, found[match][key])
                    )


class Test_TreeHandler__detranslate_tree(unittest.TestCase):

    def test_no_change(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((Chris,Bruce),Tom);"
        newtree = "tree a = ((Chris,Bruce),Tom);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree, \
            "Unable to correctly NOT translate a simple tree"

    def test_no_change_branchlengths(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
        newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree, \
            "Unable to correctly NOT translate a tree with branchlengths"

    def test_change(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((0,1),2);"
        newtree = "tree a = ((Chris,Bruce),Tom);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree, \
            "Unable to correctly detranslate a simple tree"

    def test_change_branchlengths(self):
        translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
        oldtree = "tree a = ((0:0.1,1:0.2):0.3,2:0.4);"
        newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree, \
            "Unable to correctly detranslate a tree with branchlengths"

    def test_BEAST_format(self):
        translatetable = {'1': 'Chris', '2': 'Bruce', '3': 'Tom'}
        oldtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((1:[&rate=1.0]48.056,3:[&rate=1.0]48.056):[&rate=1.0]161.121,2:[&rate=1.0]209.177);"
        newtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((Chris:[&rate=1.0]48.056,Tom:[&rate=1.0]48.056):[&rate=1.0]161.121,Bruce:[&rate=1.0]209.177);"
        trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
        assert trans == newtree, \
            "Unable to correctly detranslate a BEAST tree"


#class Test_Inline_Comments(unittest.TestCase):
    #def setUp(self):
    #    self.nex = NexusReader(
    #        os.path.join(EXAMPLE_DIR, 'example-comments.nex')
    #    )
    #
    #def test_whole_file_comments(self):
    #    assert self.nex.comments == ['[one]']
    #
    #def test_taxa_comments(self):
    #    assert self.nex.blocks['data'].comments == ['[two]'], \
    #        self.nex.data.comments
    #
    #def test_trees_comments(self):
    #    assert self.nex.blocks['characters'].comments == ['[three]']

if __name__ == '__main__':
    unittest.main()
