import pytest

from nexus import NexusReader
from nexus.tools.multistatise import multistatise


@pytest.fixture
def nex():
    res = NexusReader.from_string("""
        Begin data;
        Dimensions ntax=4 nchar=4;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              1000
        Simon              0100
        Betty              0010
        Louise             0001
        ;""")
    return multistatise(res)


def test_nexusreader_transformation(nex):
    assert isinstance(nex, NexusReader), "Nexus_obj should be a NexusReader instance"


def test_block_find(nex):
    assert 'data' in nex.blocks


def test_ntaxa_recovery(nex):
    assert nex.data.ntaxa == 4


def test_nchar_recovery(nex):
    assert nex.data.nchar == 1


def test_matrix(nex):
    assert nex.data.matrix['Harry'] == ['A'], nex.data.matrix
    assert nex.data.matrix['Simon'] == ['B'], nex.data.matrix
    assert nex.data.matrix['Betty'] == ['C'], nex.data.matrix
    assert nex.data.matrix['Louise'] == ['D'], nex.data.matrix


def test_regression_include_invisible_taxa():
    """Include taxa that have no entries"""
    data = """
    #NEXUS
    
    BEGIN DATA;
        DIMENSIONS  NTAX=15 NCHAR=7;
        FORMAT DATATYPE=STANDARD MISSING=? GAP=- INTERLEAVE=YES;
    MATRIX
    
    Gertrude                0000001
    Debbie                  0001000
    Zarathrustra            0000000
    Christie                0010000
    Benny                   0100000
    Bertha                  0100000
    Craig                   0010000
    Fannie-May              0000010
    Charles                 0010000
    Annik                   1000000
    Frank                   0000010
    Amber                   1000000
    Andreea                 1000000
    Edward                  0000100
    Donald                  0001000
    ;
    END;
    """

    nex = NexusReader.from_string(data)
    msnex = multistatise(nex)

    for taxon, sites in msnex.data.matrix.items():
        if taxon[0] == 'Z':
            continue  # will check later

        # first letter of taxa name is the expected character state
        assert taxon[0] == sites[0], \
            "%s should be %s not %s" % (taxon, taxon[0], sites[0])
    # deal with completely missing taxa
    assert 'Zarathrustra' in msnex.data.matrix
    assert msnex.data.matrix['Zarathrustra'][0] == '?'


def test_error_on_too_many_states():
    nex = NexusReader.from_string("""
    Begin data;
    Dimensions ntax=1 nchar=30;
    Format datatype=standard symbols="01" gap=-;
    Matrix
    A   111111111111111111111111111111
    ;""")
    with pytest.raises(ValueError):
        multistatise(nex)
