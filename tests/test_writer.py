import re
import pathlib

import pytest

from nexus.writer import NexusWriter


@pytest.fixture
def writer():
    data = {
        'char1': {'French': 1, 'English': 2, 'Latin': 3},
        'char2': {'French': 4, 'English': 5, 'Latin': 6},
    }
    res = NexusWriter()
    for char in data:
        for taxon, value in data[char].items():
            res.add(taxon, char, value)
    return res


def test_invalid():
    w = NexusWriter()
    with pytest.raises(ValueError):
        w.write()


def test_mixed_type_characters():
    n = NexusWriter()
    n.add('taxon1', 'Character1', 'A')
    n.add('taxon2', 'Character1', 'C')
    n.add('taxon3', 'Character1', 'A')
    with pytest.raises(AssertionError):
        n.add('taxon1', 2, 1, check=True)


def test_generic_format(writer):
    assert writer.make_nexus().startswith('#NEXUS')


def test_char_adding1(writer):
    """Test Character Addition 1"""
    assert writer.data['char1']['French'] == '1'
    assert writer.data['char1']['English'] == '2'
    assert writer.data['char1']['Latin'] == '3'


def test_char_adding2(writer):
    """Test Character Addition 2"""
    assert writer.data['char2']['French'] == '4'
    assert writer.data['char2']['English'] == '5'
    assert writer.data['char2']['Latin'] == '6'


def test_char_adding_integer(writer):
    """Test Character Addition as integer"""
    writer.add('French', 'char3', 9)
    writer.add('English', 'char3', '9')
    assert writer.data['char3']['French'] == '9'
    assert writer.data['char3']['French'] == '9'


def test_characters(writer):
    assert 'char1' in writer.characters
    assert 'char2' in writer.characters


def test_taxa(writer):
    assert 'French' in writer.taxa
    assert 'English' in writer.taxa
    assert 'Latin' in writer.taxa


def test_remove(writer):
    writer.remove("French", "char2")
    assert 'French' not in writer.data['char2']
    assert 'French' in writer.taxa


def test_remove_character(writer):
    writer.remove_character("char2")
    assert len(writer.characters) == 1
    assert 'char2' not in writer.data


def test_remove_taxon(writer):
    writer.remove_taxon("French")
    assert 'French' not in writer.taxa
    for char in writer.data:
        assert 'French' not in writer.data[char]
    n = writer.make_nexus(interleave=False)
    assert re.search("DIMENSIONS NTAX=2 NCHAR=2;", n)
    assert 'French' not in n


def test_nexus_noninterleave(writer):
    """Test Nexus Generation - Non-Interleaved"""
    n = writer.make_nexus(interleave=False)
    assert re.search(r"#NEXUS", n)
    assert re.search(r"BEGIN DATA;", n)
    assert re.search(r"DIMENSIONS NTAX=3 NCHAR=2;", n)
    assert re.search(r"MATRIX", n)
    assert re.search(r"Latin\s+36", n)
    assert re.search(r"French\s+14", n)
    assert re.search(r"English\s+25", n)
    assert re.search(r"FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
    assert re.search(r"FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] \
        == 'STANDARD'
    assert re.search(r'FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] \
        == '123456'


def test_nexus_charblock(writer):
    """Test Nexus Generation - with characters block"""
    n = writer.make_nexus(charblock=True)
    assert re.search(r"#NEXUS", n)
    assert re.search(r"BEGIN DATA;", n)
    assert re.search(r"DIMENSIONS NTAX=3 NCHAR=2;", n)
    assert re.search(r"CHARSTATELABELS", n)
    assert re.search(r"1 char1,", n)
    assert re.search(r"2 char2", n)
    assert re.search(r"MATRIX", n)
    assert re.search(r"Latin\s+36", n)
    assert re.search(r"French\s+14", n)
    assert re.search(r"English\s+25", n)
    assert re.search(r"FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
    assert re.search(r"FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] \
        == 'STANDARD'
    assert re.search(r'FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] \
        == '123456'


def test_nexus_interleave(writer):
    """Test Nexus Generation - Interleaved"""
    n = writer.make_nexus(interleave=True)
    assert re.search(r"#NEXUS", n)
    assert re.search(r"BEGIN DATA;", n)
    assert re.search(r"DIMENSIONS NTAX=3 NCHAR=2;", n)
    assert re.search(r"MATRIX", n)
    # char1
    assert re.search(r"Latin\s+3", n)
    assert re.search(r"French\s+1", n)
    assert re.search(r"English\s+2", n)
    # char2
    assert re.search(r"Latin\s+6", n)
    assert re.search(r"French\s+4", n)
    assert re.search(r"English\s+5", n)

    assert re.search(r"FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
    assert re.search(r"FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] == \
        'STANDARD'
    assert re.search(r"FORMAT.*(INTERLEAVE)", n).groups()[0] == \
        'INTERLEAVE'
    assert re.search(r'FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] == \
        '123456'


def test_polymorphic_characters(writer):
    writer.add("French", "char1", 2)
    assert writer.data['char1']['French'] == "12"
    n = writer.make_nexus(charblock=True)
    assert re.search(r"DIMENSIONS NTAX=3 NCHAR=2;", n)  # no change
    assert re.search(r"French\s+\(12\)4", n)


def test_write_to_file(writer, tmpdir):
    tmp = pathlib.Path(str(tmpdir.join('f.nex')))
    writer.write_to_file(tmp)
    assert tmp.is_file()

    n = tmp.read_text(encoding='utf8')
    assert re.search(r"#NEXUS", n)
    assert re.search(r"BEGIN DATA;", n)
    assert re.search(r"DIMENSIONS NTAX=3 NCHAR=2;", n)
    assert re.search(r"MATRIX", n)
    assert re.search(r"Latin\s+36", n)
    assert re.search(r"French\s+14", n)
    assert re.search(r"English\s+25", n)
    assert re.search(r"FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
    assert re.search(r"FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] \
        == 'STANDARD'
    assert re.search(r'FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] \
        == '123456'


def test_write_as_table(writer):
    content = writer.write_as_table()
    assert re.search(r"Latin\s+36", content)
    assert re.search(r"French\s+14", content)
    assert re.search(r"English\s+25", content)
    assert len(content.split("\n")) == 3


def test_write_as_table_with_polymorphoc(writer):
    writer.add('French', 'char1', '2')
    content = writer.write_as_table()
    assert re.search(r"Latin\s+36", content)
    assert re.search(r"French\s+\(12\)4", content)
    assert re.search(r"English\s+25", content)
    assert len(content.split("\n")) == 3


def test_make_treeblock(writer):
    writer.trees.append('tree tree1 = (French,(English,Latin));')
    writer.trees.append('tree tree2 = ((French,English),Latin);')
    treeblock = writer.make_treeblock()
    assert re.search(r"tree tree1 = \(French,\(English,Latin\)\);", treeblock)
    assert re.search(r'tree tree2 = \(\(French,English\),Latin\);', treeblock)


def test_write_with_trees(writer):
    writer.trees.append('tree tree1 = (French,(English,Latin));')
    writer.trees.append('tree tree2 = ((French,English),Latin);')
    content = writer.write()
    assert re.search(r"BEGIN TREES", content)
    assert re.search(r"tree tree1 = \(French,\(English,Latin\)\);", content)
    assert re.search(r'tree tree2 = \(\(French,English\),Latin\);', content)


def test_ntrees(writer):
    assert writer.ntrees == 0
    writer.trees.append('tree tree1 = (French,English,Latin);')
    assert writer.ntrees == 1
    writer.trees.append('tree tree2 = (French,English,Latin);')
    assert writer.ntrees == 2


def test_write_with_no_data_but_trees():
    nex = NexusWriter()
    nex.trees.append('tree tree1 = (French,(English,Latin));')
    content = nex.write()
    assert re.search(r"BEGIN TREES", content)
    assert re.search(r"tree tree1 = \(French,\(English,Latin\)\);", content)


def test_regression_format_string_has_datatype_first(writer):
    """
    Regression: Format string should contain 'datatype' as the first
    element
    """
    # SplitsTree complains otherwise.
    out = writer.make_nexus()
    assert "FORMAT DATATYPE=STANDARD" in out
    assert 'SYMBOLS="123456"' in out
