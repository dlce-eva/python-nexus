import re
import pathlib

from nexus.__main__ import main


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
