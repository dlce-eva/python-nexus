import os
import re
import unittest
from tempfile import NamedTemporaryFile
from nexus.writer import NexusWriter

data = {
    'char1': {'French': 1, 'English': 2, 'Latin': 3},
    'char2': {'French': 4, 'English': 5, 'Latin': 6},
}


class Test_NexusWriter(unittest.TestCase):
    def setUp(self):
        self.nex = NexusWriter()
        for char in data:
            for taxon, value in data[char].items():
                self.nex.add(taxon, char, value)
    
    def test_char_adding1(self):
        """Test Character Addition 1"""
        assert self.nex.data['char1']['French'] == '1'
        assert self.nex.data['char1']['English'] == '2'
        assert self.nex.data['char1']['Latin'] == '3'

    def test_char_adding2(self):
        """Test Character Addition 2"""
        assert self.nex.data['char2']['French'] == '4'
        assert self.nex.data['char2']['English'] == '5'
        assert self.nex.data['char2']['Latin'] == '6'
    
    def test_char_adding_integer(self):
        """Test Character Addition as integer"""
        self.nex.add('French', 'char3', 9)
        self.nex.add('English', 'char3', '9')
        assert self.nex.data['char3']['French'] == '9'
        assert self.nex.data['char3']['French'] == '9'
    
    def test_characters(self):
        assert 'char1' in self.nex.characters
        assert 'char2' in self.nex.characters
        
    def test_taxa(self):
        assert 'French' in self.nex.taxa
        assert 'English' in self.nex.taxa
        assert 'Latin' in self.nex.taxa
    
    def test_remove(self):
        self.nex.remove("French", "char2")
        assert 'French' not in self.nex.data['char2']
        assert 'French' in self.nex.taxa
        
    def test_remove_character(self):
        self.nex.remove_character("char2")
        assert len(self.nex.characters) == 1
        assert 'char2' not in self.nex.data
        
    def test_remove_taxon(self):
        self.nex.remove_taxon("French")
        assert 'French' not in self.nex.taxa
        for char in self.nex.data:
            assert 'French' not in self.nex.data[char]
        n = self.nex.make_nexus(interleave=False)
        assert re.search("DIMENSIONS NTAX=2 NCHAR=2;", n)
        assert 'French' not in n
        
    def test_nexus_noninterleave(self):
        """Test Nexus Generation - Non-Interleaved"""
        n = self.nex.make_nexus(interleave=False)
        assert re.search("#NEXUS", n)
        assert re.search("BEGIN DATA;", n)
        assert re.search("DIMENSIONS NTAX=3 NCHAR=2;", n)
        assert re.search("MATRIX", n)
        assert re.search("Latin\s+36", n)
        assert re.search("French\s+14", n)
        assert re.search("English\s+25", n)
        assert re.search("FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
        assert re.search("FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] \
            == 'STANDARD'
        assert re.search('FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] \
            == '123456'

    def test_nexus_charblock(self):
        """Test Nexus Generation - with characters block"""
        n = self.nex.make_nexus(charblock=True)
        assert re.search("#NEXUS", n)
        assert re.search("BEGIN DATA;", n)
        assert re.search("DIMENSIONS NTAX=3 NCHAR=2;", n)
        assert re.search("CHARSTATELABELS", n)
        assert re.search("1 char1,", n)
        assert re.search("2 char2", n)
        assert re.search("MATRIX", n)
        assert re.search("Latin\s+36", n)
        assert re.search("French\s+14", n)
        assert re.search("English\s+25", n)
        assert re.search("FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
        assert re.search("FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] \
            == 'STANDARD'
        assert re.search('FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] \
            == '123456'

    def test_nexus_interleave(self):
        """Test Nexus Generation - Interleaved"""
        n = self.nex.make_nexus(interleave=True)
        assert re.search("#NEXUS", n)
        assert re.search("BEGIN DATA;", n)
        assert re.search("DIMENSIONS NTAX=3 NCHAR=2;", n)
        assert re.search("MATRIX", n)
        # char1
        assert re.search("Latin\s+3", n)
        assert re.search("French\s+1", n)
        assert re.search("English\s+2", n)
        # char2
        assert re.search("Latin\s+6", n)
        assert re.search("French\s+4", n)
        assert re.search("English\s+5", n)

        assert re.search("FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
        assert re.search("FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] == \
            'STANDARD'
        assert re.search("FORMAT.*(INTERLEAVE)", n).groups()[0] == \
            'INTERLEAVE'
        assert re.search('FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] == \
            '123456'
            
    def test_polymorphic_characters(self):
        self.nex.add("French", "char1", 2)
        self.assertEqual(self.nex.data['char1']['French'], "12")
        n = self.nex.make_nexus(charblock=True)
        assert re.search("DIMENSIONS NTAX=3 NCHAR=2;", n)  # no change
        assert re.search("French\s+\(12\)4", n)
    
    def test_write_to_file(self):
        tmp = NamedTemporaryFile(delete=False, suffix=".nex")
        tmp.close()
        self.nex.write_to_file(tmp.name)
        assert os.path.isfile(tmp.name)
        
        with open(tmp.name, 'r') as handle:
            n = handle.read()
            
        assert re.search("#NEXUS", n)
        assert re.search("BEGIN DATA;", n)
        assert re.search("DIMENSIONS NTAX=3 NCHAR=2;", n)
        assert re.search("MATRIX", n)
        assert re.search("Latin\s+36", n)
        assert re.search("French\s+14", n)
        assert re.search("English\s+25", n)
        assert re.search("FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
        assert re.search("FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] \
            == 'STANDARD'
        assert re.search('FORMAT.*SYMBOLS\="(\d+)";', n).groups()[0] \
            == '123456'
        
        os.unlink(tmp.name)        # cleanup

    def test_write_as_table(self):
        content = self.nex.write_as_table()
        assert re.search("Latin\s+36", content)
        assert re.search("French\s+14", content)
        assert re.search("English\s+25", content)
        assert len(content.split("\n")) == 3
        
    def test_write_as_table_with_polymorphoc(self):
        self.nex.add('French', 'char1', '2')
        content = self.nex.write_as_table()
        assert re.search("Latin\s+36", content)
        assert re.search("French\s+\(12\)4", content)
        assert re.search("English\s+25", content)
        assert len(content.split("\n")) == 3
        

class RegressionTests(unittest.TestCase):
    def test_regression_format_string_has_datatype_first(self):
        """
        Regression: Format string should contain 'datatype' as the first
        element
        """
        # SplitsTree complains otherwise.
        nex = NexusWriter()
        for char, b in data.items():
            for taxon, value in b.items():
                nex.add(taxon, char, value)
        out = nex.make_nexus()
        assert "FORMAT DATATYPE=STANDARD" in out

    def test_regression_format_string_has_quoted_symbols(self):
        """Regression: Symbols in the format string should be quoted"""
        nex = NexusWriter()
        for char, b in data.items():
            for taxon, value in b.items():
                nex.add(taxon, char, value)
        out = nex.make_nexus()
        assert 'SYMBOLS="123456"' in out
