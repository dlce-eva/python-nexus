import re
import pathlib

import pytest

from nexus.__main__ import main


def _make_nexus(tmpdir, block):
    n = pathlib.Path(str(tmpdir)) / 't.nex'
    n.write_text('#NEXUS\n\n' + block, encoding='utf8')
    return n


def test_check(capsys, examples):
    main(['check', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert '0 errors' in out


def test_tally(capsys, examples):
    main(['tally', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert '- 0:  0 1' in out

    main(['tally', '-t', 'binary', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert '2\t2' in out


def test_describecharacter(capsys, examples):
    main(['describecharacter', '0', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert 'Harry, Simon' in out


def test_describetaxa(capsys, examples):
    main(['describetaxa', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert '0 x 1, 1 x 1' in out


def test_edit(capsys, examples, tmpdir):
    with pytest.raises(ValueError):
        main(['edit', '-c', str(examples / 'example2.nex')])

    main(['edit', '--number', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert '0/2' in out

    main(['edit', '--stats', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert '1x2' in out

    nex = _make_nexus(
        tmpdir,
    """Begin data;
Dimensions ntax=4 nchar=5;
Format datatype=standard symbols="01" gap=-;
Matrix
Harry              10-10
Simon              10-01
Betty              10-10
Louise             11-01
    ;
End;""")
    main(['edit', '-c', '-u', '-z', '-x', '4', str(nex)])
    out, _ = capsys.readouterr()
    assert 'NCHAR=1' in out


@pytest.mark.parametrize(
    'trees,options,check',
    [
        (
            ['tree1', 'tree2', 'tree3'],
            ['-d', '1,3'],
            lambda o: ('tree1' not in o) and ('tree2' in o) and ('tree3' not in o)),
        (
                ['tree1', 'tree2', 'tree3'],
                ['-r', '3'],
                lambda o: ('tree1' not in o) and ('tree2' not in o) and ('tree3' in o)),
        (
                ['tree1', 'tree2', 'tree3'],
                ['-n', '2'],
                lambda o: len(re.findall('tree[0-9]', o)) == 2),
        (
                ['tree1', 'tree2', 'tree3'],
                ['-c', '-t'],
                lambda o: '[comment]' not in o),
    ]
)
def test_trees(trees, options, check, capsys, tmpdir):
    trees = ['tree {0} = (a[comment]);'.format(t) for t in trees]
    n = _make_nexus(tmpdir, 'begin trees;\n{0}\nend;\n'.format('\n'.join(trees)))
    main(['trees', str(n)] + options)
    out, _ = capsys.readouterr()
    assert check(out)


def test_combine(capsys, tmpdir, examples):
    o = tmpdir.join('out.nex')
    main(['combine', '-o', str(o), str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert 'out.nex' in out


def test_randomise(capsys, examples):
    main(['randomise', '-n', '10', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert re.search('[01]{10}', out)


def test_binary2multistate(capsys, examples):
    main(['binary2multistate', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert 'BEGIN DATA' in out


def test_convert(capsys, examples):
    main(['convert', str(examples / 'example.nex')])
    out, _ = capsys.readouterr()
    assert '>Betty' in out


def test_deinterleave(capsys, tmpdir):
    M = """
    begin data;
       dimensions ntax=4 nchar=20;
       format datatype=dna gap=- interleave=yes;
       matrix
       taxon_1 AACGATTCGT
       taxon_2 AAGGAT--CA
       taxon_3 AACGACTCCT
       taxon_4 AAGGATTCCT

       taxon_1 TTTTCGAAGC
       taxon_2 TTTTCGGAGC
       taxon_3 TTTTTGATGC
       taxon_4 TTTTCGGAGC
       ;
    end;
    """
    in_ = pathlib.Path(str(tmpdir)) / 'in.nex'
    in_.write_text(M, encoding='utf8')
    main(['deinterleave', str(in_)])
    out, _ = capsys.readouterr()
    assert 'taxon_1 AACGATTCGTTTTTCGAAGC' in out


def test_multistate2binary(capsys, tmpdir):
    M = """
        Begin data;
        Dimensions ntax=3 nchar=2;
        Format datatype=standard symbols="01" gap=-;
        Charstatelabels
            1 char1, 2 char2;
        Matrix
        Maori               14
        Dutch               25
        Latin               36
        ;"""
    in_ = pathlib.Path(str(tmpdir)) / 'in.nex'
    in_.write_text(M, encoding='utf8')
    main(['multistate2binary', str(in_)])
    out, _ = capsys.readouterr()
    assert '100100' in out
