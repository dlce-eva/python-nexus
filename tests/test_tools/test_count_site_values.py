import pytest

from nexus import NexusReader
from nexus.tools import count_site_values


def test_errorcheck():
    with pytest.raises(TypeError):
        count_site_values("I am a string")
    with pytest.raises(TypeError):
        count_site_values(0)


def test_errorcheck_characters(nex):
    with pytest.raises(TypeError):
        count_site_values(nex, None)


def test_count_missing_one(nex):
    missing = count_site_values(nex)
    for taxon in missing:
        assert missing[taxon] == 0


def test_count_missing_two():
    expected = {
        'Harry': 0, 'Simon': 1, 'Peter': 1, 'Betty': 2, 'Louise': 3
    }
    nexus = NexusReader.from_string("""#NEXUS
    Begin data;
    Dimensions ntax=5 nchar=3;
    Format datatype=standard symbols="01" gap=-;
    Matrix
    Harry              010  [No missing]
    Simon              0?0  [one missing]
    Peter              0-0  [one gap]
    Betty              ?-1  [one gap and one missing = 2 missing]
    Louise             ???  [three missing]
        ;
    End;
    """)
    missing = count_site_values(nexus)
    for taxon in missing:
        assert missing[taxon] == expected[taxon]


def test_count_other_values_one():
    expected = {
        'Harry': 1, 'Simon': 1, 'Peter': 0, 'Betty': 0, 'Louise': 0
    }
    nexus = NexusReader.from_string("""#NEXUS
    Begin data;
    Dimensions ntax=5 nchar=3;
    Format datatype=standard symbols="01" gap=-;
    Matrix
    Harry              0A0  [No missing]
    Simon              0A0  [one missing]
    Peter              0-0  [one gap]
    Betty              ?-1  [one gap and one missing = 2 missing]
    Louise             ???  [three missing]
        ;
    End;
    """)
    count = count_site_values(nexus, 'A')
    for taxon in count:
        assert count[taxon] == expected[taxon]


def test_count_other_values_two():
    expected = {
        'Harry': 1, 'Simon': 2, 'Peter': 1, 'Betty': 0, 'Louise': 0
    }
    nexus = NexusReader.from_string("""#NEXUS
    Begin data;
    Dimensions ntax=5 nchar=3;
    Format datatype=standard symbols="01" gap=-;
    Matrix
    Harry              0A0  [No missing]
    Simon              0AB  [one missing]
    Peter              0-B  [one gap]
    Betty              ?-1  [one gap and one missing = 2 missing]
    Louise             ???  [three missing]
        ;
    End;
    """)
    count = count_site_values(nexus, ['A', 'B'])
    for taxon in count:
        assert count[taxon] == expected[taxon]
