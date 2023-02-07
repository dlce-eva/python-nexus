import types

import pytest

from nexus.parser import Nexus, TokenType


@pytest.mark.parametrize(
    'nex,expect,roundtrip',
    [
        (
            """#NEXUS
BEGIN TREES;
TREE best = (fish , (frog,
(snake, mouse))) ;
END;""",
            lambda n: sum(1 for t in n.nexus if t.type != TokenType.WHITESPACE) == 23,
            True),
        (
            '#NEXUS begin trees; tree ; end;',
            lambda n: n.blocks[0].name == 'TREES',
            True),
        (
            "#NEXUS BEGIN AssuMP[co[mm]ent]TiONS; END;",
            lambda n: n.blocks[0].name == 'ASSUMPTIONS' and n.comments[0].text == 'co[mm]ent',
            False),  # We cannot roundtrip in-word comments!
        # Commands cannot contain semicolons, except as terminators, unless the semicolons are
        # contained within a comment or within a quoted token consisting of more than one text
        # character.
        (
            "#NEXUS cmd [;] stuff;",
            lambda n: n.commands[0].words[1].text == 'stuff',
            True),
        (
            "#NEXUS cmd 'a;b' stuff;",
            lambda n: n.commands[0].words[1].text == 'stuff',
            True),
        (
            "#NEXUS cmd '[ab]' stuff;",
            lambda n: not n.comments,
            True),
        # Single quotes in quoted words must be doubled:
        (
            "#NEXUS cmd 'a''b' stuff;",
            lambda n: "a'b" in [t.text for t in n.commands[0]],
            True),
    ]
)
def test_Nexus(nex, expect, roundtrip):
    n = Nexus(nex)
    assert expect(types.SimpleNamespace(
        nexus=n,
        commands=list(n.iter_commands()),
        blocks=list(n.iter_blocks()),
        comments=list(n.iter_comments()),
    ))
    if roundtrip:
        assert str(n) == nex
