"""Tests for nexus checkers"""
from nexus.reader import NexusReader
from nexus.checker import BEASTAscertainmentChecker
from nexus.checker import DuplicateLabelChecker
from nexus.checker import EmptyCharacterChecker
from nexus.checker import LabelChecker
from nexus.checker import LowStateCountChecker
from nexus.checker import PotentiallyUnsafeTaxaLabelsChecker
from nexus.checker import SingletonCharacterChecker
from nexus.checker import UnusualStateChecker


def test_DuplicateLabelChecker():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
	    charstatelabels
            1  CHAR,
            2  CHAR_A,
            3  CHAR
        ;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              001
        B              001
        C              001
        ;
    """)
    c = DuplicateLabelChecker(nex)
    assert len(c.errors) == 1


def test_LabelChecker():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
	    charstatelabels
            1  CHAR_A,
            2  CHAR_B
        ;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              001
        B              001
        C              001
        ;
    """)
    c = LabelChecker(nex)
    assert len(c.errors) == 1


def test_LabelChecker_no_error_with_no_labels():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              001
        B              001
        C              001
        ;
    """)
    c = LabelChecker(nex)
    assert len(c.errors) == 0


def test_PotentiallyUnsafeTaxaLabelsChecker():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        Dimensions ntax=2 nchar=1;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Hary               1
        Harr!              1
        ;
    """)

    c = PotentiallyUnsafeTaxaLabelsChecker(nex)
    assert len(c.errors) == 1


def test_EmptyCharacterChecker():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              101
        B              101
        C              000
        ;
    """)
    c = EmptyCharacterChecker(nex)
    assert len(c.errors) == 1


def test_EmptyCharacterChecker_ignore_ascert():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        charstatelabels
            1  CHAR_ascertainement,
            2  CHAR_A,
            3  CHAR_B
        ;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              001
        B              001
        C              001
        ;
    """)
    c = EmptyCharacterChecker(nex, verbose=True)
    assert len(c.errors) == 1  # and not two!
    assert len(c.messages) == 1


def test_SingletonCharacterChecker():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              101
        B              001
        C              010
        ;
    """)
    c = SingletonCharacterChecker(nex)
    assert len(c.errors) == 2


def test_LowStateCountChecker():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        Dimensions ntax=7 nchar=50;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              11111111111111111111111111111111111111111111111111
        B              11111111111111111111111111111111111111111111111111
        C              11111111111111111111111111111111111111111111111111
        D              11111111111111111111111111111111111111111111111111
        E              11111111111111111111111111111111111111111111111111
        F              11111111111111111111111111111111111111111111111111
        G              00000000000000000000000000000000000000000000000001
        ;
    """)
    LowStateCountChecker.THRESHOLD = 1
    c = LowStateCountChecker(nex)
    assert len(c.errors) == 1


def test_UnusualStateChecker():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              111
        B              000
        C              00A
        ;
    """)
    UnusualStateChecker.THRESHOLD = 0.3
    c = UnusualStateChecker(nex)
    assert len(c.errors) == 1


def test_BEASTAscertainmentCheckersingle_ascertainment_ok():
    # All ok with one labelled ascertainment character
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        charstatelabels
            1  CHAR_ascertainement,
            2  CHAR_A,
            3  CHAR_B
        ;
        Dimensions ntax=3 nchar=3;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              011
        B              011
        C              001
        ;
    """)
    c = BEASTAscertainmentChecker(nex)
    assert len(c.errors) == 0


def test_BEASTAscertainmentCheckerfail_with_no_assumptions_block():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        charstatelabels
            1  CHAR_A_ascertainement,
            2  CHAR_A,
            3  CHAR_B_ascertainement,
            4  CHAR_B
        ;
        Dimensions ntax=3 nchar=4;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              0101
        B              0101
        C              0001
        ;
    """)
    c = BEASTAscertainmentChecker(nex)
    assert len(c.errors) == 1


def test_BEASTAscertainmentChecker_ok():
    # fail with two
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        charstatelabels
            1  CHAR_A_ascertainement,
            2  CHAR_A,
            3  CHAR_B_ascertainement,
            4  CHAR_B
        ;
        Dimensions ntax=3 nchar=4;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              0101
        B              0101
        C              0001
        ;
    
        begin assumptions;
            charset A = 1-2;
            charset B = 3-4;
        end;
    """)
    c = BEASTAscertainmentChecker(nex)
    assert len(c.errors) == 0


def test_BEASTAscertainmentChecker_fail_with_non_empty():
    # fail with two
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        charstatelabels
            1  CHAR_A_ascertainement,
            2  CHAR_A,
            3  CHAR_B_ascertainement,
            4  CHAR_B
        ;
        Dimensions ntax=3 nchar=4;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        A              0101
        B              0101
        C              10?1
        ;
    begin assumptions;
        charset A = 1-2;
        charset B = 3-4;
    end;
    """)
    c = BEASTAscertainmentChecker(nex)
    assert len(c.errors) == 1  # should ONLY be one
