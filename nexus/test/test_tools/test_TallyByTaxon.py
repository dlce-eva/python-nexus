import unittest

from nexus import NexusReader
from nexus.tools.sites import tally_by_taxon

class Test_TallyByTaxon(unittest.TestCase):
    """Test combine_nexuses"""
    def setUp(self):
        self.nex = NexusReader()
        self.nex.read_string(
            """Begin data;
            Dimensions ntax=3 nchar=6;
            Format datatype=standard symbols="12" gap=-;
            Matrix
            Harry              0111-?
            Simon              0011-?
            Elvis              0001-?
            ;"""
        )
    
    def test_errorcheck(self):
        self.assertRaises(TypeError, tally_by_taxon, "I am a string")
        self.assertRaises(TypeError, tally_by_taxon, 0)
    
    def test_tally_by_taxon(self):
        tally = tally_by_taxon(self.nex)
        # sites that are zero
        assert tally['Harry']['0'] == [0]
        assert tally['Simon']['0'] == [0, 1]
        assert tally['Elvis']['0'] == [0, 1, 2]
        
        # sites that are 1
        assert tally['Harry']['1'] == [1, 2, 3]
        assert tally['Simon']['1'] == [2, 3]
        assert tally['Elvis']['1'] == [3]
        
        # sites that are -
        assert tally['Harry']['-'] == [4]
        assert tally['Simon']['-'] == [4]
        assert tally['Elvis']['-'] == [4]
        
        # sites that are ?
        assert tally['Harry']['?'] == [5]
        assert tally['Simon']['?'] == [5]
        assert tally['Elvis']['?'] == [5]
