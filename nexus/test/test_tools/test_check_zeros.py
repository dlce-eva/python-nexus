import unittest

from nexus import NexusReader
from nexus.tools.check_zeros import check_zeros, remove_zeros


class Test_CheckZeros(unittest.TestCase):
    """Test multistatise"""
    def setUp(self):
        self.nex = NexusReader()
        self.nex.read_string("""
        Begin data;
        Dimensions ntax=4 nchar=8;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        [                  01234567]
        Harry              01000000
        Simon              0010000-
        Betty              00010-0?
        Louise             000010?0
        ;""")
        self.found = check_zeros(self.nex)
    
    def test_find_zero(self):
        self.assertIn(0, self.found)
    
    def test_find_missing_dash(self):
        self.assertIn(5, self.found)
    
    def test_find_missing_questionmark(self):
        self.assertIn(6, self.found)
    
    def test_find_complex(self):
        self.assertIn(7, self.found)
    
    def test_change_missing(self):
        found = check_zeros(self.nex, missing=['-'])
        assert found == [0, 5]
    
    def test_change_absence(self):
        found = check_zeros(self.nex, absences=['1', '0'])
        assert found == [0, 1, 2, 3, 4, 5, 6, 7]
    
    def test_remove_zeros(self):
        new = remove_zeros(self.nex)
        assert new.data.nchar == 4
        assert new.data.matrix['Harry'] == ['1', '0', '0', '0']
        assert new.data.matrix['Simon'] == ['0', '1', '0', '0']
        assert new.data.matrix['Betty'] == ['0', '0', '1', '0']
        assert new.data.matrix['Louise'] == ['0', '0', '0', '1']

if __name__ == '__main__':
    unittest.main()
