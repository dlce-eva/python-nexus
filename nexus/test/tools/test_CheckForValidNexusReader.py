import os
import nose

from nexus import NexusReader, NexusWriter, NexusFormatException
from nexus.tools import check_for_valid_NexusReader

EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], '../examples')

class Test_CheckForValidNexusReader:
    """Test check_for_valid_NexusReader"""
    
    def test_valid_NexusReader(self):
        check_for_valid_NexusReader(NexusReader())
    
    @nose.tools.raises(TypeError)
    def test_failure_on_nonnexus_1(self):
        check_for_valid_NexusReader("i am not a nexus")
    
    @nose.tools.raises(TypeError)
    def test_failure_on_nonnexus_2(self):
        check_for_valid_NexusReader(1)
        
    @nose.tools.raises(TypeError)
    def test_failure_on_nonnexus_3(self):
        check_for_valid_NexusReader([1,2,3])
    
    @nose.tools.raises(NexusFormatException)
    def test_failure_on_required_block_twod_block_one(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        check_for_valid_NexusReader(nexus, ['trees'])
    
    @nose.tools.raises(NexusFormatException)
    def test_failure_on_required_block_two(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        check_for_valid_NexusReader(nexus, ['r8s'])
    
    def test_valid_with_required_block_one(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        check_for_valid_NexusReader(nexus, ['data'])
        
    def test_valid_with_required_block_two(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))
        check_for_valid_NexusReader(nexus, ['data', 'taxa'])
