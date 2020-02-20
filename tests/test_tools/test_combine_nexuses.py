import re

import pytest

from nexus import NexusReader
from nexus.tools.combine_nexuses import combine_nexuses


@pytest.fixture
def nex1():
    res = NexusReader.from_string("""Begin data;
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="12" gap=-;
            Matrix
            Harry              1
            Simon              2
            ;""")
    # set short_filename to test that functionality. If `combine_nexuses`
    # doesn't use `short_filename`, then the nex1 characters will be
    # identified as 1.xx, rather than 0.xx
    res.short_filename = '0'
    return res


@pytest.fixture
def nex2():
    return NexusReader.from_string("""Begin data;
            Dimensions ntax=2 nchar=1;
            Format datatype=standard symbols="34" gap=-;
            Matrix
            Harry              3
            Simon              4
            ;"""
    )


@pytest.fixture
def nex3():
    return NexusReader.from_string("""Begin data;
            Dimensions ntax=3 nchar=1;
            Format datatype=standard symbols="345" gap=-;
            Matrix
            Betty              3
            Boris              4
            Simon              5
            ;""")


def test_failure_on_nonlist_1():
    with pytest.raises(TypeError):
        combine_nexuses("I am not a list")


def test_failure_on_nonlist_2():
    with pytest.raises(TypeError):
        combine_nexuses(["hello"])


def test_combine_simple(nex1, nex2):
    newnex = combine_nexuses([nex1, nex2])
    assert newnex.data['0.1']['Harry'] == '1'
    assert newnex.data['0.1']['Simon'] == '2'
    assert newnex.data['2.1']['Harry'] == '3'
    assert newnex.data['2.1']['Simon'] == '4'


def test_combine_simple_generated_matrix(nex1, nex2):
    newnex = combine_nexuses([nex1, nex2]).write()
    assert re.search(r"""\bSimon\s+24\b""", newnex)
    assert re.search(r"""\bHarry\s+13\b""", newnex)


def test_combine_simple_generated_formatline(nex1, nex2):
    newnex = combine_nexuses([nex1, nex2]).write()
    assert re.search(r"""\bNTAX=2\b""", newnex)
    assert re.search(r"""\bNCHAR=2\b""", newnex)
    assert re.search(r'\sSYMBOLS="1234"[\s;]', newnex)


def test_combine_missing(nex1, nex3):
    newnex = combine_nexuses([nex1, nex3])
    assert newnex.data['0.1']['Harry'] == '1'
    assert newnex.data['0.1']['Simon'] == '2'
    assert newnex.data['2.1']['Betty'] == '3'
    assert newnex.data['2.1']['Boris'] == '4'


def test_combine_missing_generated_matrix(nex1, nex3):
    newnex = combine_nexuses([nex1, nex3]).write()
    assert re.search(r"""\bSimon\s+25\b""", newnex)
    assert re.search(r"""\bHarry\s+1\\?\b""", newnex)
    assert re.search(r"""\bBetty\s+\?3\b""", newnex)
    assert re.search(r"""\bBoris\s+\?4\b""", newnex)


def test_combine_missing_generated_formatline(nex1, nex3):
    newnex = combine_nexuses([nex1, nex3]).write()
    assert re.search(r"""\bNTAX=4\b""", newnex)
    assert re.search(r"""\bNCHAR=2\b""", newnex)
    assert re.search(r'\sSYMBOLS="12345"[\s;]', newnex)


def test_combine_with_character_labels():
    n1 = NexusReader.from_string("""
        BEGIN DATA;
            DIMENSIONS NTAX=3 NCHAR=3;
            FORMAT DATATYPE=STANDARD MISSING=0 GAP=-  SYMBOLS="123";
            CHARSTATELABELS
                1 char1,
                2 char2,
                3 char3
        ;
        MATRIX
        Tax1         123
        Tax2         123
        Tax3         123
        ;
        """)
    n2 = NexusReader.from_string("""
        BEGIN DATA;
            DIMENSIONS NTAX=3 NCHAR=3;
            FORMAT DATATYPE=STANDARD MISSING=0 GAP=-  SYMBOLS="456";
            CHARSTATELABELS
                1 char1,
                2 char2,
                3 char3
        ;
        MATRIX
        Tax1         456
        Tax2         456
        Tax3         456
        ;
        """)
    newnex = combine_nexuses([n1, n2])
    assert re.search(r"""\bNTAX=3\b""", newnex.write())
    assert re.search(r"""\bNCHAR=6\b""", newnex.write())
    assert re.search(r'\sSYMBOLS="123456"[\s;]', newnex.write())

    for tax in [1, 2, 3]:
        assert re.search(r"""\bTax%d\s+123456\b""" % tax, newnex.write())

    counter = 1
    for nex_id in [1, 2]:
        for char_id in [1, 2, 3]:
            assert re.search(
                r"""\b%d\s+%d.char%d\b""" % (counter, nex_id, char_id),
                newnex.write(charblock=True)
            )
            counter += 1


def test_combine():
    nex1 = NexusReader.from_string("""Begin trees;
            tree 1 = (a,b,c);
        end;""")
    nex2 = NexusReader.from_string("""Begin trees;
            tree 2 = (b,a,c);
            tree 3 = (b,c,a);
        end;""")

    newnex = combine_nexuses([nex1, nex2])
    assert len(newnex.trees) == 3
    assert newnex.trees[0] == "tree 1 = (a,b,c);"
    assert newnex.trees[1] == "tree 2 = (b,a,c);"
    assert newnex.trees[2] == "tree 3 = (b,c,a);"
