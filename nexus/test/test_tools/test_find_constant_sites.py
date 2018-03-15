import os
import unittest

from nexus import NexusReader
from nexus.tools import find_constant_sites

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../../examples')


class Test_FindConstantSites(unittest.TestCase):
    def test_find_constant_sites_1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert not find_constant_sites(nexus)

    def test_find_constant_sites_2(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        const = find_constant_sites(nexus)
        assert len(const) == 4
        assert 0 in const
        assert 1 in const
        assert 2 in const
        assert 3 in const
