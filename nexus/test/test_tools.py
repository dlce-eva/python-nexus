"""Tests for utils in bin directory"""
import os
import re

import nose

from nexus import NexusReader, NexusWriter, NexusFormatException
from nexus.tools import *
from nexus.bin.nexus_treemanip import run_resample

EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'examples')

class Test_CombineNexuses:
    """Test combine_nexuses"""
    def setup(self):
        self.nex1 = NexusReader()
        self.nex1.read_string(
            """Begin data;
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="12" gap=-;
            Matrix
            Harry              1
            Simon              2
            ;"""
        )
        self.nex2 = NexusReader()
        self.nex2.read_string(
            """Begin data;
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="34" gap=-;
            Matrix
            Harry              3
            Simon              4
            ;"""
        )
        self.nex3 = NexusReader()
        self.nex3.read_string(
            """Begin data;
            Dimensions ntax=3 nchar=1;
            Format datatype=standard symbols="345" gap=-;
            Matrix
            Betty              3
            Boris              4
            Simon              5
            ;"""
        )
    
    @nose.tools.raises(TypeError)
    def test_failure_on_nonlist_1(self):
        combine_nexuses("i am not a list")
        
    @nose.tools.raises(TypeError)
    def test_failure_on_nonlist_2(self):
        combine_nexuses("i am not a list")
    
    @nose.tools.raises(TypeError)
    def test_failure_on_nonlist_3(self):
        combine_nexuses(["hello",]) # should be NexusReader instances
        
    def test_combine_simple(self):
        newnex = combine_nexuses([self.nex1, self.nex2])
        assert newnex.data['1.1']['Harry'] == '1'
        assert newnex.data['1.1']['Simon'] == '2'
        assert newnex.data['2.1']['Harry'] == '3'
        assert newnex.data['2.1']['Simon'] == '4'
    
    def test_combine_simple_generated_matrix(self):
        newnex = combine_nexuses([self.nex1, self.nex2])
        assert re.search(r"""\bSimon\s+24\b""", newnex.write())
        assert re.search(r"""\bHarry\s+13\b""", newnex.write())
    
    def test_combine_simple_generated_formatline(self):
        newnex = combine_nexuses([self.nex1, self.nex2])
        assert re.search(r"""\bNTAX=2\b""", newnex.write())
        assert re.search(r"""\bNCHAR=2\b""", newnex.write())
        assert re.search(r'\sSYMBOLS="1234"[\s;]', newnex.write())
        
    def test_combine_missing(self):
        newnex = combine_nexuses([self.nex1, self.nex3])
        print newnex.data
        assert newnex.data['1.1']['Harry'] == '1'
        assert newnex.data['1.1']['Simon'] == '2'
        assert newnex.data['2.1']['Betty'] == '3'
        assert newnex.data['2.1']['Boris'] == '4'
        
    def test_combine_missing_generated_matrix(self):
        newnex = combine_nexuses([self.nex1, self.nex3])
        assert re.search(r"""\bSimon\s+25\b""", newnex.write())
        assert re.search(r"""\bHarry\s+1\\?\b""", newnex.write())
        assert re.search(r"""\bBetty\s+\?3\b""", newnex.write())
        assert re.search(r"""\bBoris\s+\?4\b""", newnex.write())
        
    def test_combine_missing_generated_formatline(self):
        newnex = combine_nexuses([self.nex1, self.nex3])
        assert re.search(r"""\bNTAX=4\b""", newnex.write())
        assert re.search(r"""\bNCHAR=2\b""", newnex.write())
        assert re.search(r'\sSYMBOLS="12345"[\s;]', newnex.write())

    def test_combine_with_character_labels(self):
        n1 = NexusReader()
        n1.read_string(
            """
            BEGIN DATA;
                DIMENSIONS NTAX=3 NCHAR=3;
                FORMAT DATATYPE=STANDARD MISSING=0 GAP=-  SYMBOLS="123";
                CHARSTATELABELS
            		1 char1,
            		2 char2,
            		3 char3
            ;
            MATRIX
            Tax1         123
            Tax2         123
            Tax3         123
            ;
            """
        )
        n2 = NexusReader()
        n2.read_string(
            """
            BEGIN DATA;
                DIMENSIONS NTAX=3 NCHAR=3;
                FORMAT DATATYPE=STANDARD MISSING=0 GAP=-  SYMBOLS="456";
                CHARSTATELABELS
            		1 char1,
            		2 char2,
            		3 char3
            ;
            MATRIX
            Tax1         456
            Tax2         456
            Tax3         456
            ;
            """
        )
        newnex = combine_nexuses([n1, n2])
        assert re.search(r"""\bNTAX=3\b""", newnex.write())
        assert re.search(r"""\bNCHAR=6\b""", newnex.write())
        assert re.search(r'\sSYMBOLS="123456"[\s;]', newnex.write())
        
        for tax in [1,2,3]:
            assert re.search(r"""\bTax%d\s+123456\b""" % tax, newnex.write())
        
        counter = 1
        for nex_id in [1,2]:
            for char_id in [1,2,3]:
                assert re.search(
                    r"""\b%d\s+%d.char%d\b""" % (counter, nex_id, char_id), 
                    newnex.write(charblock=True)
                )
                counter += 1

class Test_ShuffleNexus:
    """Test shufflenexus"""
    def setup(self):
        self.nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        shufflenexus({})

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        shufflenexus("I AM NOT A NEXUS")

    def test_output(self):
        nexus = shufflenexus(self.nexus)
        assert isinstance(nexus, NexusWriter)

    @nose.tools.raises(ValueError)
    def test_resample_errorcheck_ok_1(self):
        shufflenexus(self.nexus, "STRING")

    @nose.tools.raises(ValueError)
    def test_resample_errorcheck_2(self):
        shufflenexus(self.nexus, 0)

    def test_resample_10(self):
        nexus = shufflenexus(self.nexus, 10)
        assert len(nexus.characters) == 10
        assert sorted(nexus.taxalist) == ['George', 'John', 'Paul', 'Ringo']

    def test_resample_100(self):
        nexus = shufflenexus(self.nexus, 100)
        assert len(nexus.characters) == 100
        assert sorted(nexus.taxalist) == ['George', 'John', 'Paul', 'Ringo']


class Test_CountMissings:
    """Test count_missing_sites"""
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus(self):
        count_missing_sites({})

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        count_missing_sites("I AM NOT A NEXUS")

    def test_count_missings_1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        missing = count_missing_sites(nexus)
        for taxon in missing:
            assert missing[taxon] == 0

    def test_count_missings_2(self):
        expected = {'Harry': 0, 'Simon': 1, 'Peter': 1, 'Betty': 2, 'Louise': 3}
        nexus = NexusReader()
        nexus.read_string("""#NEXUS 
        Begin data;
        Dimensions ntax=4 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              010  [No missing]
        Simon              0?0  [one missing]
        Peter              0-0  [one gap]
        Betty              ?-1  [one gap and one missing = 2 missing]
        Louise             ???  [three missing]
            ;
        End;
        """)
        missing = count_missing_sites(nexus)
        for taxon in missing:
            assert missing[taxon] == expected[taxon]


class Test_FindConstantSites:
    """Test find_constant_sites"""
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        find_constant_sites({})

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        find_constant_sites("I AM NOT A NEXUS")

    def test_find_constant_sites_1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert len(find_constant_sites(nexus)) == 0

    def test_find_constant_sites_2(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        const = find_constant_sites(nexus)
        assert len(const) == 4
        assert 0 in const
        assert 1 in const
        assert 2 in const
        assert 3 in const


class Test_FindUniqueSites:
    """Test find_unique_sites"""
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        find_unique_sites({})

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        find_unique_sites("I AM NOT A NEXUS")

    def test_find_unique_sites_1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert len(find_unique_sites(nexus)) == 0

    def test_find_unique_sites_2(self):
        nexus = NexusReader()
        nexus.read_string("""Begin data;
        Dimensions ntax=4 nchar=7;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              10000?-
        Simon              1100011
        Betty              1110000
        Louise             1111000
        ;""")
        unique = find_unique_sites(nexus)

        # site 1 should NOT be in the uniques (3x1 and 1x0)
        # - i.e. are we ignoring sites with ONE absent taxon
        assert 1 not in unique
        # these should also NOT be in unique
        assert 0 not in unique
        assert 2 not in unique
        assert 4 not in unique # constant
        # site 3 is a simple unique site - check we found it
        assert 3 in unique
        # sites 5 and 6 should also be unique 
        # - are we handling missing data appropriately?
        assert 5 in unique
        assert 6 in unique


class Test_new_nexus_without_sites:

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        new_nexus_without_sites({}, [])

    def test_remove_sites_1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        nexus = new_nexus_without_sites(nexus, [1])
        assert len(nexus.data) == 1
    
    
class Test_multistatise:
    """Test multistatise"""
    def setup(self):
        self.nex = NexusReader()
        self.nex.read_string(
        """Begin data;
        Dimensions ntax=4 nchar=4;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              1000
        Simon              0100
        Betty              0010
        Louise             0001
        ;""")
        self.nex = multistatise(self.nex)
        
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        multistatise({})
    
    def test_nexusreader_transformation(self):
        assert isinstance(self.nex, NexusReader), "Nexus_obj should be a NexusReader instance"
        
    def test_block_find(self):
        assert 'data' in self.nex.blocks
    
    def test_ntaxa_recovery(self):
        assert self.nex.data.ntaxa == 4
        
    def test_nchar_recovery(self):
        assert self.nex.data.nchar == 1
        
    def test_matrix(self):
        assert self.nex.data.matrix['Harry'][0] == 'A'
        assert self.nex.data.matrix['Simon'][0] == 'B'
        assert self.nex.data.matrix['Betty'][0] == 'C'
        assert self.nex.data.matrix['Louise'][0] == 'D'
    
    
    def test_regression_include_invisible_languages(self):
        """Include languages that have no entries"""
        data = """
        #NEXUS
        
        BEGIN DATA;
            DIMENSIONS  NTAX=34 NCHAR=7;
            FORMAT DATATYPE=STANDARD MISSING=? GAP=- INTERLEAVE=YES;
        MATRIX
        
        Gertrude                0000001
        Debbie                  0001000
        Zarathrustra            0000000
        Christie                0010000
        Benny                   0100000
        Bertha                  0100000
        Craig                   0010000
        Fannie-May              0000010
        Charles                 0010000
        Annik                   1000000
        Frank                   0000010
        Amber                   1000000
        Andreea                 1000000
        Edward                  0000100
        Donald                  0001000
        ;
        END;
        """
        
        nex = NexusReader()
        nex.read_string(data)
        msnex = multistatise(nex)
        
        for taxon,sites in msnex.data.matrix.items():
            if taxon[0] == 'Z':
                continue # will check later
            
            # first letter of taxa name is the expected character state
            assert taxon[0] == sites[0], "%s should be %s not %s" % (taxon, taxon[0], sites[0])
        print msnex.data.matrix
        # deal with completely missing taxa
        assert 'Zarathrustra' in msnex.data.matrix
        assert msnex.data.matrix['Zarathrustra'][0] == '?'
        
        
class Test_ResampleTrees:
    """Test nexus_treemanip.run_resample"""
    def setup(self):
        self.nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
        
    @nose.tools.raises(NexusFormatException)
    def test_failure_on_no_treeblock(self):
        run_resample(1, NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex')))
        
    def test_resample(self):
        newnex = run_resample(2, self.nexus)
        assert len(newnex.trees.trees) == 1
        
    def test_resample_one(self):
        newnex = run_resample(1, self.nexus)
        assert len(newnex.trees.trees) == 3
        
    