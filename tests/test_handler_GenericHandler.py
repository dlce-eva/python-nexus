"""Tests for GenericHandler"""
from nexus.reader import NexusReader, GenericHandler


def test_remove_comments():
    assert GenericHandler().remove_comments("bootstrap [bootstrap!]") == 'bootstrap '


def test_generic_readwrite():
    expected = [
        "begin sets;",
        "    A = 1;",
        "    B = 2;",
        "end;",
    ]
    nex = NexusReader.from_string("\n".join(expected))
    for line in nex.sets.write().split("\n"):
        if line:
            e = expected.pop(0).strip()
            assert line.strip() == e


def test_write_produces_end():
    nex = NexusReader.from_string("""
        begin assumptions;
            A = 1;
        end;
    """)
    assert "end;" in nex.write()
