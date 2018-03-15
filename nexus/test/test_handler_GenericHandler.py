"""Tests for GenericHandler"""
import os
import unittest
from nexus.reader import NexusReader, GenericHandler

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')

class Test_GenericHandler(unittest.TestCase):
    def test_remove_comments(self):
        assert GenericHandler().remove_comments("bootstrap [bootstrap!]") == 'bootstrap '

    def test_generic_readwrite(self):
        expected = """Begin data;
        Dimensions ntax=4 nchar=2;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              00
        Simon              01
        Betty              10
        Louise             11
        ;
        """.split("\n")
        nex = NexusReader()
        nex.handlers['data'] = GenericHandler
        nex.read_file(os.path.join(EXAMPLE_DIR, 'example.nex'))
        for line in nex.data.write().split("\n"):
            e = expected.pop(0).strip()
            assert line.strip() == e
