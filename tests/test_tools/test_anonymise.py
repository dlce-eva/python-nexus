"""Tests for utils in bin directory"""
import pytest

from nexus import NexusReader
from nexus.bin.nexus_anonymise import anonymise, hash


def test_anonymise_taxa(nex):
    nex = anonymise(nex, salt="test")
    for old_taxon in ['Harry', 'Simon', 'Betty', 'Louise']:
        assert old_taxon not in nex.data.matrix, \
            '%s should have been anonymised' % old_taxon

    assert nex.data.matrix[hash("test", "Betty")] == \
        ['1', '0']
    assert nex.data.matrix[hash("test", "Harry")] == \
        ['0', '0']
    assert nex.data.matrix[hash("test", "Simon")] == \
        ['0', '1']
    assert nex.data.matrix[hash("test", "Louise")] == \
        ['1', '1']


def test_anonymise_data_with_labels(nex2):
    nex = anonymise(nex2,  salt="test")
    for old_taxon in ['John', 'Paul', 'George', 'Ringo']:
        assert old_taxon not in nex.data.matrix, \
            '%s should have been anonymised' % old_taxon
        h = hash("test", old_taxon)
        # check data block
        assert h in nex.data.matrix, "Missing %s" % h
        assert nex.data.matrix[h] == ['a', 'c', 't', 'g']
        # check taxa block
        assert h in nex.taxa.taxa


def test_anonymise_data_with_interleave(nex3):
    nex = anonymise(nex3, salt="test")
    for old_taxon in ['Harry', 'Simon']:
        assert old_taxon not in nex.data.matrix, \
            '%s should have been anonymised' % old_taxon
        h = hash("test", old_taxon)
        assert h in nex.data.matrix
        assert h in nex.data.taxa
        assert nex.data.matrix[h] == ['0', '1', '2', '3', '4', '5']


def test_notimplemented_exception():
    with pytest.raises(NotImplementedError):
        nex = NexusReader.from_string(
            """Begin something;
            Dimensions ntax=5 nchar=1;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              1
            ;""")
        anonymise(nex)


def test_notimplemented_exception_untranslated_trees(trees):
    with pytest.raises(NotImplementedError):
        anonymise(trees)


def test_anonymise_translated_trees(trees_translated):
    nex = anonymise(trees_translated, salt="test")
    expected = [
        'Chris', 'Bruce', 'Tom', 'Henry', 'Timothy',
        'Mark', 'Simon', 'Fred', 'Kevin', 'Roger',
        'Michael', 'Andrew', 'David'
    ]
    assert len(nex.trees.taxa) == len(expected)
    for taxon in expected:
        hashtaxon = hash("test", taxon)
        assert hashtaxon in nex.trees.taxa


def test_anonymise_beast_treefile(trees_beast):
    nex = anonymise(trees_beast, salt="test")
    expected = [
        "R1", "B2", "S3", "T4", "A5", "E6", "U7", "T8", "T9", "F10", "U11",
        "T12", "N13", "F14", "K15", "N16", "I17", "L18", "S19", "T20",
        "V21", "R22", "M23", "H24", "M25", "M26", "M27", "R28", "T29",
        "M30", "P31", "T32", "R33", "P34", "R35", "W36", "F37", "F38"
    ]
    for taxon in expected:
        h = hash("test", taxon)
        # check taxa block
        assert taxon not in nex.taxa.taxa, \
            '%s should have been anonymised' % taxon
        assert h in nex.taxa.taxa

        # check trees block
        assert taxon not in nex.trees.taxa, \
            '%s should have been anonymised' % taxon
        assert h in nex.trees.taxa


def test_anonymise_characters(examples):
    nex = anonymise(NexusReader(examples / 'example-characters.nex'), salt="test")

    expected_taxa = ['A', 'B', 'C', 'D', 'E']
    for taxon in expected_taxa:
        h = hash("test", taxon)
        # check taxa block
        assert taxon not in nex.taxa.taxa, \
            '%s should have been anonymised' % taxon
        assert h in nex.taxa.taxa

        # check characters block
        assert taxon not in nex.data.taxa, \
            '%s should have been anonymised' % taxon
        assert h in nex.data.taxa
