import os

import nose

from nexus import NexusReader, NexusWriter, NexusFormatException
from nexus.tools import shufflenexus

EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], '../examples')

class Test_ShuffleNexus:
    """Test shufflenexus"""
    def setup(self):
        self.nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))

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


