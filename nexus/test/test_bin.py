"""Tests for utils in bin directory"""
import os
import nose

from nexus import NexusReader, NexusWriter
from nexus.bin.calc_missings import count_missings
from nexus.bin.remove_constantchars import find_constant_sites
from nexus.bin.randomise import shufflenexus
from nexus.bin.remove_uniquechars import find_unique_sites


EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'examples')

class Test_count_missings:
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus1(self):
        count_missings({})
        
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus2(self):
        count_missings("I AM NOT A NEXUS")
        
    def test_count_missings_one(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        missing = count_missings(nexus)
        for taxon in missing:
            assert missing[taxon] == 0
    
    def test_count_missings_two(self):
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
        missing = count_missings(nexus)
        for taxon in missing:
            assert missing[taxon] == expected[taxon]


class Test_shufflenexus:
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus1(self):
        shufflenexus({})
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus2(self):
        shufflenexus("I AM NOT A NEXUS")
    
    def test_constant(self):
        # shuffling a constant character is not going to do anything...
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        nexus = shufflenexus(nexus)
        for char, expected_value in {'0': 'a', '1': 'c', '2':'t', '3':'g'}.items():
            for taxon, shuffled_value in nexus.data[char].items():
                assert shuffled_value == expected_value
    
    def test_output(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        nexus = shufflenexus(nexus)
        assert isinstance(nexus, NexusWriter)
        

class Test_find_constant_sites:
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus1(self):
        find_constant_sites({})
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus2(self):
        find_constant_sites("I AM NOT A NEXUS")
    
    def test_find_constant_sites1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert len(find_constant_sites(nexus)) == 0
    
    def test_find_constant_sites2(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        const = find_constant_sites(nexus)
        assert len(const) == 4
        assert 0 in const
        assert 1 in const
        assert 2 in const
        assert 3 in const
    

class Test_find_unique_sites:

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus1(self):
        find_unique_sites({})

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus2(self):
        find_unique_sites("I AM NOT A NEXUS")

    def test_find_unique_sites1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert len(find_unique_sites(nexus)) == 0

    def test_find_unique_sites2(self):
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
        
        
        