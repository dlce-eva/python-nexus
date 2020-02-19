import unittest

from nexus import NexusReader
from nexus.tools.sites import tally_by_site

class Test_TallyBySite(unittest.TestCase):
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
        self.assertRaises(TypeError, tally_by_site, "I am a string")
        self.assertRaises(TypeError, tally_by_site, 0)
    
    def test_tally_by_site(self):
        tally = tally_by_site(self.nex)
        # 000
        assert 'Harry' in tally[0]['0']
        assert 'Simon' in tally[0]['0']
        assert 'Elvis' in tally[0]['0']
        # 100
        assert 'Harry' in tally[1]['1']
        assert 'Simon' in tally[1]['0']
        assert 'Elvis' in tally[1]['0']
        # 110
        assert 'Harry' in tally[2]['1']
        assert 'Simon' in tally[2]['1']
        assert 'Elvis' in tally[2]['0']
        # 111
        assert 'Harry' in tally[3]['1']
        assert 'Simon' in tally[3]['1']
        assert 'Elvis' in tally[3]['1']
        # ---
        assert 'Harry' in tally[4]['-']
        assert 'Simon' in tally[4]['-']
        assert 'Elvis' in tally[4]['-']
        # ???
        assert 'Harry' in tally[5]['?']
        assert 'Simon' in tally[5]['?']
        assert 'Elvis' in tally[5]['?']
