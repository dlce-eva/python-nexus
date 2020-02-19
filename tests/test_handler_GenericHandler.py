"""Tests for GenericHandler"""
import os
import unittest
from nexus.reader import NexusReader, GenericHandler

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')

class Test_GenericHandler(unittest.TestCase):
    def test_remove_comments(self):
        assert GenericHandler().remove_comments("bootstrap [bootstrap!]") == 'bootstrap '

    def test_generic_readwrite(self):
        expected = [
            "begin sets;",
            "    A = 1;",
            "    B = 2;",
            "end;",
        ]
        nex = NexusReader()
        nex.read_string("\n".join(expected))
        for line in nex.sets.write().split("\n"):
            e = expected.pop(0).strip()
            assert line.strip() == e

    def test_write_produces_end(self):
        nex = NexusReader()
        nex.read_string("""
            begin assumptions;
                A = 1;
            end;
        """)
        assert "end;" in nex.write()
