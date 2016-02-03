"""Tests for utils in bin directory"""
import os
import unittest

from nexus import NexusReader
from nexus.bin.nexus_treemanip import run_resample

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../../examples')

class Test_ResampleTrees(unittest.TestCase):
    def setUp(self):
        self.nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
        
    def test_resample(self):
        newnex = run_resample(2, self.nexus)
        assert len(newnex.trees.trees) == 1
        
    def test_resample_one(self):
        newnex = run_resample(1, self.nexus)
        assert len(newnex.trees.trees) == 3
    
    def test_raises_error_on_invalid_resample_value(self):
        with self.assertRaises(ValueError):
            run_resample('a', self.nexus)
        with self.assertRaises(ValueError):
            run_resample(None, self.nexus)
        with self.assertRaises(ValueError):
            run_resample([], self.nexus)
        
        

if __name__ == '__main__':
    unittest.main()
