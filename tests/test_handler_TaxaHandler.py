"""Tests for TaxaHandler"""
import pytest

from nexus.reader import NexusReader
from nexus.handlers.taxa import TaxaHandler
from nexus.exceptions import NexusFormatException

expected = ['John', 'Paul', 'George', 'Ringo']
    

def test_block_find(nex2):
    assert 'taxa' in nex2.blocks

def test_taxa(nex2):
    for taxon in expected:
        assert taxon in nex2.data.matrix
        assert taxon in nex2.blocks['taxa'].taxa
    assert nex2.blocks['taxa'].ntaxa == len(expected)


def test_iterable(nex2):
    for idx, taxa in enumerate(nex2.blocks['taxa']):
        assert taxa == expected[idx]


def test_wrap_label_in_quotes_only_when_needed(nex2):
    nex2.taxa.taxa[0] = "long name"
    output = nex2.taxa.write()
    assert "[1] 'long name'" in output
    assert "[2] Paul" in output
    assert "[3] George" in output
    assert "[4] Ringo" in output


def test_write_produces_end(nex2):
    assert "end;" in nex2.taxa.write()


def test_error_on_incorrect_dimensions():
    with pytest.raises(NexusFormatException):
        NexusReader.from_string("""
        #NEXUS
    
        begin taxa;
          dimensions ntax=2;
          taxlabels A B C;
        end;
        """)


def test_annotation_read():
    nex = NexusReader.from_string("""
    #NEXUS
    BEGIN TAXA;
        DIMENSIONS  NTAX=3;
        TAXLABELS
        A[&!color=#aaaaaa]
        B[&!color=#bbbbbb]
        C[&!color=#cccccc]
    END;
    """)
    nex.taxa.annotations['A'] = '[&!color=#aaaaaa]'
    nex.taxa.annotations['B'] = '[&!color=#bbbbbb]'
    nex.taxa.annotations['C'] = '[&!color=#cccccc]'

    out = nex.taxa.write()
    assert 'A[&!color=#aaaaaa]' in out
    assert 'B[&!color=#bbbbbb]' in out
    assert 'C[&!color=#cccccc]' in out


def test_annotation_write(nex2):
    nex2.taxa.annotations['John'] = '[&!color=#006fa6]'
    assert 'John[&!color=#006fa6]' in nex2.taxa.write()


def test_complicated_name():
    h = list(TaxaHandler()._parse_taxa('test[&!color=#000000,!name="taxon label"]'))
    assert len(h) == 1
    assert h[0][0] == 'test'
    assert h[0][1] == '[&!color=#000000,!name="taxon label"]'
    