"""Tests for utils in bin directory"""
import os
import re

import nose

from nexus import NexusReader, NexusWriter
from nexus.bin.nexus_combine_nexus import combine_nexuses
from nexus.bin.nexus_randomise import shufflenexus

EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'examples')

class Test_CombineNexuses:
    
    def setup(self):
        self.nex1 = NexusReader()
        self.nex1.read_string(
            """Begin data;
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="12" gap=-;
            Matrix
            Harry              1
            Simon              2
            ;"""
        )
        self.nex2 = NexusReader()
        self.nex2.read_string(
            """Begin data;
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="34" gap=-;
            Matrix
            Harry              3
            Simon              4
            ;"""
        )
        self.nex3 = NexusReader()
        self.nex3.read_string(
            """Begin data;
            Dimensions ntax=3 nchar=1;
            Format datatype=standard symbols="345" gap=-;
            Matrix
            Betty              3
            Boris              4
            Simon              5
            ;"""
        )
    
    @nose.tools.raises(TypeError)
    def test_failure_on_nonlist_1(self):
        combine_nexuses("i am not a list")
        
    @nose.tools.raises(TypeError)
    def test_failure_on_nonlist_2(self):
        combine_nexuses("i am not a list")
    
    @nose.tools.raises(TypeError)
    def test_failure_on_nonlist_3(self):
        combine_nexuses(["hello",]) # should be NexusReader instances
        
    def test_combine_simple(self):
        newnex = combine_nexuses([self.nex1, self.nex2])
        assert newnex.data['1']['Harry'] == '1'
        assert newnex.data['1']['Simon'] == '2'
        assert newnex.data['2']['Harry'] == '3'
        assert newnex.data['2']['Simon'] == '4'
    
    def test_combine_simple_generated_matrix(self):
        newnex = combine_nexuses([self.nex1, self.nex2])
        assert re.search(r"""\bSimon\s+24\b""", newnex.write())
        assert re.search(r"""\bHarry\s+13\b""", newnex.write())
    
    def test_combine_simple_generated_formatline(self):
        newnex = combine_nexuses([self.nex1, self.nex2])
        assert re.search(r"""\bNTAX=2\b""", newnex.write())
        assert re.search(r"""\bNCHAR=2\b""", newnex.write())
        assert re.search(r'\sSYMBOLS="1234"[\s;]', newnex.write())
        
    def test_combine_missing(self):
        newnex = combine_nexuses([self.nex1, self.nex3])
        assert newnex.data['1']['Harry'] == '1'
        assert newnex.data['1']['Simon'] == '2'
        assert newnex.data['2']['Betty'] == '3'
        assert newnex.data['2']['Boris'] == '4'
        
    def test_combine_missing_generated_matrix(self):
        newnex = combine_nexuses([self.nex1, self.nex3])
        assert re.search(r"""\bSimon\s+25\b""", newnex.write())
        assert re.search(r"""\bHarry\s+1\\?\b""", newnex.write())
        assert re.search(r"""\bBetty\s+\?3\b""", newnex.write())
        assert re.search(r"""\bBoris\s+\?4\b""", newnex.write())
        
    def test_combine_missing_generated_formatline(self):
        newnex = combine_nexuses([self.nex1, self.nex3])
        assert re.search(r"""\bNTAX=4\b""", newnex.write())
        assert re.search(r"""\bNCHAR=2\b""", newnex.write())
        assert re.search(r'\sSYMBOLS="12345"[\s;]', newnex.write())


class Test_ShuffleNexus:

    def setup(self):
        self.nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example2.nex'))

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        shufflenexus({})

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        shufflenexus("I AM NOT A NEXUS")

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

    