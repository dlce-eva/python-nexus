from nexus import NexusReader
from nexus.tools.sites import count_binary_set_size


def test_count_binary_set_size():
    nex = NexusReader.from_string("""Begin data;
        Dimensions ntax=3 nchar=4;
        Format datatype=standard symbols="12" gap=-;
        Matrix
        Harry              0111
        Simon              0011
        Elvis              0001
        ;""")
    tally = count_binary_set_size(nex)
    assert tally[0] == 1
    assert tally[1] == 1
    assert tally[2] == 1
    assert tally[3] == 1
