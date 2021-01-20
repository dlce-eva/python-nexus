"""Tests for nexus reading -- Maddison et al example"""
import pytest

from nexus import NexusReader


@pytest.fixture
def maddison(examples):
    return NexusReader(str(examples / 'maddison_et_al.nex'))


expected = {
    'fish': [_ for _ in 'ACATAGAGGGTACCTCTAAG'],
    'frog': [_ for _ in 'ACTTAGAGGCTACCTCTACG'],
    'snake': [_ for _ in 'ACTCACTGGGTACCTTTGCG'],
    'mouse': [_ for _ in 'ACTCAGACGGTACCTTTGCG'],
}


def test_taxa(maddison):
    assert 'taxa' in maddison.blocks
    for taxon in expected:
        assert taxon in maddison.blocks['taxa'].taxa
    assert maddison.blocks['taxa'].ntaxa == len(expected)


def test_characters(maddison):
    assert 'characters' in maddison.blocks
    assert maddison.blocks['characters'].nchar == 20
    assert maddison.blocks['characters'].ntaxa == 4
    assert maddison.blocks['characters'].format['datatype'] == 'DNA'
    for taxon in expected:
        assert taxon in maddison.blocks['characters'].matrix
        assert maddison.blocks['characters'].matrix[taxon] == expected[taxon]


def test_data(maddison):  # characters is linked to `data`
    assert maddison.blocks['data'] == maddison.blocks['characters']


def test_trees(maddison):
    assert 'trees' in maddison.blocks
    assert maddison.blocks['trees'].ntrees == 1
