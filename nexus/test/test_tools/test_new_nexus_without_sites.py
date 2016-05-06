import os
import unittest

from nexus import NexusReader
from nexus.tools import new_nexus_without_sites

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../../examples')

class Test_NewNexusWithoutSites(unittest.TestCase):
    def test_remove_sites_list(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        nexus = new_nexus_without_sites(nexus, [1])
        assert len(nexus.data) == 1
    
    def test_remove_sites_set(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        nexus = new_nexus_without_sites(nexus, set([1]))
        assert len(nexus.data) == 1


if __name__ == '__main__':
    unittest.main()
