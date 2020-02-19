import unittest

from nexus import NexusReader
from nexus.tools.sites import count_binary_set_size

class Test_CountBinarySetSize(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader()
        self.nex.read_string(
            """Begin data;
            Dimensions ntax=3 nchar=4;
            Format datatype=standard symbols="12" gap=-;
            Matrix
            Harry              0111
            Simon              0011
            Elvis              0001
            ;"""
        )
    
    def test_errorcheck(self):
        self.assertRaises(TypeError, count_binary_set_size, "I am a string")
        self.assertRaises(TypeError, count_binary_set_size, 0)
    
    def test_count_binary_set_size(self):
        tally = count_binary_set_size(self.nex)
        assert tally[0] == 1
        assert tally[1] == 1
        assert tally[2] == 1
        assert tally[3] == 1
