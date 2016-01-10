import os
import unittest

from nexus import NexusReader, NexusWriter
from nexus.tools.shufflenexus import shufflenexus

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../../examples')

class Test_ShuffleNexus(unittest.TestCase):
    def setUp(self):
        self.nexus_obj = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
    
    def test_output(self):
        nexus_obj = shufflenexus(self.nexus_obj)
        assert isinstance(nexus_obj, NexusWriter)
    
    def test_exception_resample_noninteger(self):
        self.assertRaises(ValueError, shufflenexus, self.nexus_obj, 'a')
        
    def test_exception_resample_badinteger(self):
        self.assertRaises(ValueError, shufflenexus, self.nexus_obj, 0)
    
    def test_exception_resample_negativeinteger(self):
        self.assertRaises(ValueError, shufflenexus, self.nexus_obj, -1)
    
    def test_exception_nexus_obj_1(self):
        self.assertRaises(TypeError, shufflenexus, "I am a string")
    
    def test_exception_nexus_obj_2(self):
        self.assertRaises(TypeError, shufflenexus, 0)
        
    def test_resample_1(self):
        nexus_obj = shufflenexus(self.nexus_obj, 1)
        assert len(nexus_obj.characters) == 1
        assert sorted(nexus_obj.taxa) == \
            ['George', 'John', 'Paul', 'Ringo']
    
    def test_resample_10(self):
        nexus_obj = shufflenexus(self.nexus_obj, 10)
        assert len(nexus_obj.characters) == 10
        assert sorted(nexus_obj.taxa) == \
            ['George', 'John', 'Paul', 'Ringo']
    
    def test_resample_100(self):
        nexus_obj = shufflenexus(self.nexus_obj, 100)
        assert len(nexus_obj.characters) == 100
        assert sorted(nexus_obj.taxa) == \
            ['George', 'John', 'Paul', 'Ringo']



if __name__ == '__main__':
    unittest.main()
