import types

import pytest

from nexus.parser import Nexus, TokenType


@pytest.mark.parametrize(
    'nex,expect',
    [
        (
            """#NEXUS
BEGIN TREES;
TREE best = (fish , (frog,
(snake, mouse))) ;
END;""",
            lambda n: sum(1 for t in n.nexus if t.type != TokenType.WHITESPACE) == 23),
        (
            '#NEXUS begin trees; tree ; end;',
            lambda n: n.blocks[0].name == 'TREES'),
        (
            "#NEXUS BEGIN AssuMP[co[mm]ent]TiONS; END;",
            lambda n: n.blocks[0].name == 'ASSUMPTIONS' and n.comments[0].text == 'co[mm]ent'),
        # Commands cannot contain semicolons, except as terminators, unless the semicolons are
        # contained within a comment or within a quoted token consisting of more than one text
        # character.
        (
            "#NEXUS cmd [;] stuff;",
            lambda n: next(n.commands[0].iter_payload_tokens(TokenType.WORD)).text == 'stuff'),
        (
            "#NEXUS cmd 'a;b' stuff;",
            lambda n: next(n.commands[0].iter_payload_tokens(TokenType.WORD)).text == 'stuff'),
        (
            "#NEXUS cmd '[ab]' stuff;",
            lambda n: not n.comments),
        # Single quotes in quoted words must be doubled:
        (
            "#NEXUS cmd 'a''b' stuff;",
            lambda n: "a'b" in [t.text for t in n.commands[0]]),
        (
            "#NEXUS cmd first\tline \t\n second line;",
            lambda n: n.commands[0].payload_lines == ['first\tline', 'second line']),
        # Leave newick payload untouched.
        (
            '#NEXUS begin trees; tree (a[&comment]:1,b:2)c:3; end trees;',
            lambda n: n.blocks[0].commands['TREE'][0].payload == '(a[&comment]:1,b:2)c:3',
        ),
        # Test on "real" Nexus files:
        (
            'regression/ape_random.trees',
            lambda n: n.comments[0].text == 'R-package APE, Mon Apr  4 13:30:05 2011'),
        (
            'regression/detranslate-beast-2.trees',
            lambda n: n.blocks[0].commands['TREE'][0].payload.startswith('TREE1 = [&R] ((((4[&length')),
        (
            'examples/example.trees',
            lambda n: n.blocks[0].commands['TREE'][2].payload.endswith('David:0.3086497606)')
        )
    ]
)
def test_Nexus(nex, expect, regression, examples):
    if nex.startswith('#'):
        n = Nexus(nex)
    else:
        d, _, fname = nex.partition('/')
        p = (regression if d == 'regression' else examples) / fname
        n = Nexus.from_file(p)
        nex = p.read_text(encoding='utf8')
    assert expect(types.SimpleNamespace(
        nexus=n,
        commands=list(n.iter_commands()),
        blocks=list(n.iter_blocks()),
        comments=list(n.iter_comments()),
    ))
    assert str(n) == nex
