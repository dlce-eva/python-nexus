"""Tests for GenericHandler"""
import unittest
from nexus.reader import GenericHandler

class Test_GenericHandler(unittest.TestCase):
    def test_remove_comments(self):
        assert GenericHandler().remove_comments("bootstrap [bootstrap!]") == 'bootstrap '

if __name__ == '__main__':
    unittest.main()
