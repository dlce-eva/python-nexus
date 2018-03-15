"""Tests for nexus reading"""
import os
import gzip
import unittest
from tempfile import NamedTemporaryFile
from nexus.reader import NexusReader
from nexus.exceptions import NexusFormatException

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')

class Test_NexusReader_Core(unittest.TestCase):
    """Test the Core functionality of NexusReader"""
    def test_read_file(self):
        nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        assert 'data' in nex.blocks
        assert 'Simon' in nex.blocks['data'].matrix
    
    def test_error_on_missing_file(self):
        with self.assertRaises(IOError):
            NexusReader(os.path.join(EXAMPLE_DIR, 'sausage.nex'))
    
    def test_read_gzip_file(self):
        # first, MAKE a gzip file
        tmp = NamedTemporaryFile(delete=False, suffix=".gz")
        tmp.close()
        with open(os.path.join(EXAMPLE_DIR, 'example.nex'), 'rb') as h:
            content = h.read()
        
        with gzip.open(tmp.name, 'wb') as h:
            h.write(content)
        
        # test it's ok
        nex = NexusReader(tmp.name)
        assert 'data' in nex.blocks
        assert 'Simon' in nex.blocks['data'].matrix
        os.unlink(tmp.name)        # cleanup

    def test_read_string(self):
        handle = open(os.path.join(EXAMPLE_DIR, 'example.nex'))
        data = handle.read()
        handle.close()
        nex = NexusReader()
        nex.read_string(data)
        assert 'data' in nex.blocks
        assert 'Simon' in nex.blocks['data'].matrix
    
    def test_read_string_returns_self(self):
        nex = NexusReader().read_string(
            """
            #NEXUS
            
            Begin data;
            Dimensions ntax=1 nchar=1;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              1
            ;
        """)
        assert isinstance(nex, NexusReader)
    
    def test_write(self):
        nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
        with open(os.path.join(EXAMPLE_DIR, 'example.trees')) as handle:
            text = handle.read()
        assert text == nex.write()
    
    def test_write_to_file(self):
        tmp = NamedTemporaryFile(delete=False, suffix=".nex")
        tmp.close()
        nex = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
        nex.write_to_file(tmp.name)
        assert os.path.isfile(tmp.name)
        n2 = NexusReader(tmp.name)
        assert n2.data.matrix == nex.data.matrix
        assert sorted(n2.data.taxa) == sorted(nex.data.taxa)
        os.unlink(tmp.name)        # cleanup
    
    def test_error_on_duplicate_block(self):
        with self.assertRaises(NexusFormatException):
            NexusReader().read_string(
                """
                #NEXUS
                
                Begin data;
                Dimensions ntax=5 nchar=1;
                Format datatype=standard symbols="01" gap=-;
                Matrix
                Harry              1
                ;
                
                Begin data;
                Dimensions ntax=5 nchar=1;
                Format datatype=standard symbols="01" gap=-;
                Matrix
                Harry              1
                """)
