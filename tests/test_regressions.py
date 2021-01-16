"""Regression Tests"""
import os
import re
import unittest

import pytest

from nexus.reader import NexusReader
from nexus.handlers.data import DataHandler


@pytest.fixture
def bad_chars(regression):
    return NexusReader(regression / 'bad_chars_in_taxaname.trees')


@pytest.fixture
def with_dash(regression):
    return NexusReader(regression / 'detranslate-with-dash.trees')


@pytest.fixture
def int_length(regression):
    return NexusReader(regression / 'branchlengths-in-integers.trees')


@pytest.fixture
def mesquite(regression):
    return NexusReader(regression / 'mesquite_taxa_block.nex')


@pytest.fixture
def mesquite_branches(regression):
    return NexusReader(regression / 'mesquite_formatted_branches.trees')


def test_DataHandler_Regression_WhitespaceInMatrix_regression(regression):
    """
    Regression: Test that leading whitespace in a data matrix is parsed ok
    """
    nex = NexusReader(regression / 'white_space_in_matrix.nex')
    assert nex.blocks['data'].nchar == 2
    assert nex.blocks['data'].matrix['Harry'] == ['0', '0']
    assert nex.blocks['data'].matrix['Simon'] == ['0', '1']
    assert nex.blocks['data'].matrix['Betty'] == ['1', '0']
    assert nex.blocks['data'].matrix['Louise'] == ['1', '1']


def test_TreeHandler_Regression_RandomAPETrees_regression(regression):
    """Regression: Test that we can parse randomly generated APE/R trees"""
    nex = NexusReader(regression / 'ape_random.trees')
    assert nex.trees.ntrees == 2


def test_TreeHandler_Regression_BadCharsInTaxaName_trees(bad_chars):
    # did we get a tree block?
    assert 'trees' in bad_chars.blocks
    # did we find 3 trees?
    assert len(bad_chars.blocks['trees'].trees) == 1
    assert bad_chars.blocks['trees'].ntrees == 1


def test_TreeHandler_Regression_BadCharsInTaxaName_translation(bad_chars):
    # did we get the translation parsed properly.
    assert bad_chars.trees.was_translated
    assert len(bad_chars.trees.translators) == 5
    # check last entry
    assert bad_chars.trees.translators['5'] == 'PALAUNGWA_De.Ang'


def test_TreeHandler_Regression_BadCharsInTaxaName_detranslate(bad_chars):
    # check detranslate
    bad_chars.trees.detranslate()
    expected = '(MANGIC_Bugan,MANGIC_Paliu,MANGIC_Mang,PALAUNGWA_Danaw,PAL'
    assert expected in bad_chars.trees[0]


def test_TreeHandler_Regression_DetranslateWithDash_trees(with_dash):
    # did we get a tree block?
    assert 'trees' in with_dash.blocks
    # did we find 3 trees?
    assert len(with_dash.blocks['trees'].trees) == 1
    assert with_dash.blocks['trees'].ntrees == 1


def test_TreeHandler_Regression_DetranslateWithDash_translate(with_dash):
    # did we get the translation parsed properly.
    assert with_dash.trees.was_translated
    assert len(with_dash.trees.translators) == 5


def test_TreeHandler_Regression_DetranslateWithDash_regression(with_dash):
    # check last entry
    assert with_dash.trees.translators['4'] == 'four-1'
    assert with_dash.trees.translators['5'] == 'four_2'


def test_TreeHandler_Regression_DetranslateWithDash_detranslate(with_dash):
    # check detranslate
    with_dash.trees.detranslate()
    assert '(one,two,three,four-1,four_2)' in with_dash.trees[0]


def test_TreeHandler_Regression_BranchLengthsInIntegers_trees(int_length):
    # did we get a tree block?
    assert 'trees' in int_length.blocks
    # did we find 3 trees?
    assert len(int_length.blocks['trees'].trees) == 1
    assert int_length.blocks['trees'].ntrees == 1


def test_TreeHandler_Regression_BranchLengthsInIntegers_translation(int_length):
    # did we get the translation parsed properly.
    assert int_length.trees.was_translated
    assert len(int_length.trees.translators) == 5


def test_TreeHandler_Regression_BranchLengthsInIntegers_detranslate(int_length):
    # check detranslate
    int_length.trees.detranslate()
    assert '(one:0.1,two:0.2,three:1,four:3,five:0.3)' in int_length.trees[0]


def test_TaxaHandler_Regression_Mesquite_taxa_block(mesquite):
    """Regression: Test that we can parse MESQUITE taxa blocks"""
    for taxon in ['A', 'B', 'C']:
        assert taxon in mesquite.taxa
    # did we get the right number of taxa in the matrix?
    assert mesquite.taxa.ntaxa == len(mesquite.taxa.taxa) == 3


def test_TaxaHandler_Regression_Mesquite_taxa_block_attributes(mesquite):
    assert 'taxa' in mesquite.blocks
    assert len(mesquite.taxa.attributes) == 2
    assert 'TITLE Untitled_Block_of_Taxa;' in mesquite.taxa.attributes
    assert 'LINK Taxa = Untitled_Block_of_Taxa;' in \
        mesquite.taxa.attributes


def test_TaxaHandler_Regression_Mesquite_write(mesquite):
    expected_patterns = [
        r'^begin taxa;$',
        r'^\s+TITLE Untitled_Block_of_Taxa;$',
        r'^\s+dimensions ntax=3;$',
        r'^\s+taxlabels$',
        r"^\s+\[1\] A$",
        r"^\s+\[2\] B$",
        r"^\s+\[3\] C$",
        r'^;$',
        r'^end;$',
    ]
    written = mesquite.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected


@pytest.fixture
def mesquite_attributes():
    nex = NexusReader.from_string("""
    #NEXUS

    Begin data;
    TITLE Untitled_Block_of_Taxa;
    LINK Taxa = Untitled_Block_of_Taxa;
    Dimensions ntax=2 nchar=2;
    Format datatype=standard gap=- symbols="01";
    Matrix
    Harry              00
    Simon              01
        ;
    End;
    """)
    return nex


def test_DataHandler_Regression_Mesquite_attributes(mesquite_attributes):
    assert len(mesquite_attributes.data.attributes) == 2
    assert mesquite_attributes.data.attributes[0] == \
        """TITLE Untitled_Block_of_Taxa;"""
    assert mesquite_attributes.data.attributes[1] == \
        """LINK Taxa = Untitled_Block_of_Taxa;"""


def test_DataHandler_Regression_Mesquite_write(mesquite_attributes):
    expected_patterns = [
        r'^begin data;$',
        r'^\s+TITLE Untitled_Block_of_Taxa;$',
        r'^\s+LINK Taxa = Untitled_Block_of_Taxa;$',
        r'^\s+dimensions ntax=2 nchar=2;$',
        r'^\s+format datatype=standard gap=- symbols="01";$',
        r"^matrix$",
        r"^Harry\s+00",
        r"^Simon\s+01$",
        r'^\s+;$',
        r'^end;$',
    ]
    written = mesquite_attributes.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected


def test_TreeHandler_Regression_Mesquite_attributes(mesquite_branches):
    assert len(mesquite_branches.trees.attributes) == 2
    assert mesquite_branches.trees.attributes[0] == \
        """Title 'Trees from "temp.trees"';"""
    assert mesquite_branches.trees.attributes[1] == \
        """LINK Taxa = Untitled_Block_of_Taxa;"""


def test_TreeHandler_Regression_Mesquite_found_trees(mesquite_branches):
    assert mesquite_branches.trees.ntrees == 1


def test_TreeHandler_Regression_Mesquite_found_taxa(mesquite_branches):
    assert len(mesquite_branches.trees.taxa) == 3
    assert 'A' in mesquite_branches.trees.taxa
    assert 'B' in mesquite_branches.trees.taxa
    assert 'C' in mesquite_branches.trees.taxa


def test_TreeHandler_Regression_Mesquite_was_translated(mesquite_branches):
    assert mesquite_branches.trees.was_translated


def test_TreeHandler_Regression_Mesquite_translation(mesquite_branches):
    assert mesquite_branches.trees.translators['1'] == 'A'
    assert mesquite_branches.trees.translators['2'] == 'B'
    assert mesquite_branches.trees.translators['3'] == 'C'


def test_TreeHandler_Regression_Mesquite_write(mesquite_branches):
    written = mesquite_branches.write()
    assert """Title 'Trees from "temp.trees"';""" in written
    assert """LINK Taxa = Untitled_Block_of_Taxa;""" in written


@pytest.fixture
def taxlabels(regression):
    """
    Regression: Test that we can read taxalabels delimited by spaces not new
    lines.
    """
    return NexusReader(regression / 'taxlabels.nex')


def test_TaxaHandler_OneLine_block_find(taxlabels):
    assert 'taxa' in taxlabels.blocks
    assert 'data' in taxlabels.blocks


def test_TaxaHandler_OneLine_taxa(taxlabels):
    for taxon in ['A', 'B', 'C']:
        assert taxon in taxlabels.data.matrix
        assert taxon in taxlabels.blocks['taxa'].taxa
    assert taxlabels.blocks['taxa'].ntaxa == 3


def test_TaxaHandler_OneLine_charblock_find(taxlabels):
    assert hasattr(taxlabels.data, 'characters')


def test_TaxaHandler_OneLine_data_ntaxa(taxlabels):
    assert taxlabels.data.ntaxa == 3


def test_TaxaHandler_OneLine_data_nchar(taxlabels):
    assert taxlabels.data.nchar == 3


def test_TaxaHandler_OneLine_matrix(taxlabels):
    assert taxlabels.data.matrix["A"] == ["1", "1", "1"]
    assert taxlabels.data.matrix["B"] == ["0", "1", "1"]
    assert taxlabels.data.matrix["C"] == ["0", "0", "1"]


@pytest.fixture
def glottolog(regression):
    """
    Regression: Test that we can read glottolog tree format.
    """
    return NexusReader(regression / 'glottolog.trees')


def test_GlottologTree_block_find(glottolog):
    assert 'taxa' in glottolog.blocks
    assert 'trees' in glottolog.blocks


def test_GlottologTree_taxa(glottolog):
    for i in range(2, 6):
        taxon = 'abun125%d' % i
        assert taxon in glottolog.blocks['taxa'].taxa


def test_GlottologTree_taxa_count(glottolog):
    # has duplicate taxon label
    assert glottolog.blocks['taxa'].ntaxa == 4


def test_GlottologTree_tree_count(glottolog):
    assert len(glottolog.trees.trees) == 1
    

def test_DataHandler_NoMissingInSymbols_write():
    """
    Regression:
    Test that the missing or gap symbols are NOT in the SYMBOLS format string
    """
    nex = NexusReader.from_string("""
    #NEXUS
    begin data;
    Dimensions ntax=2 nchar=2;
    Format datatype=standard gap=- symbols="01";
    Matrix
    Harry              1-
    Simon              0?
        ;
    End;
    """)
    expected_patterns = [
        r'^begin data;$',
        r'^\s+dimensions ntax=2 nchar=2;$',
        r'^\s+format datatype=standard gap=- symbols="01";$',
        r"^matrix$",
        r"^Harry\s+1-",
        r"^Simon\s+0\?$",
        r'^\s+;$',
        r'^end;$',
    ]
    written = nex.write()
    for expected in expected_patterns:
        assert re.search(expected, written, re.MULTILINE), \
            'Expected "%s"' % expected
    

def test_DataHandler_ParsingGlitch_parse_format_line():
    """
    Regression:
    Fix for parsing glitch in DataHandler.parse_format()
    """
    d = DataHandler()
    f = d.parse_format_line('FORMAT DATATYPE=STANDARD GAP=- MISSING=? SYMBOLS = "012345";')
    assert f['datatype'] == 'standard', \
        "Expected 'standard', but got '%s'" % f['datatype']
    assert f['symbols'] == '012345', \
        "Expected '012345', but got '%s'" % f['symbols']
    assert f['gap'] == '-', \
        "Expected 'gap', but got '%s'" % f['gap']
    assert f['missing'] == '?', \
        "Expected 'gap', but got '%s'" % f['missing']


def test_TreeHandler_MrBayes(regression):
    """
    Test reading of treefile generated by a 2003-era MrBayes which, for some reason, have
    a tab between "tree\t<name>=(...)"
    """
    nex = NexusReader(regression / 'mrbayes.trees')
    assert len(nex.trees.trees) == 1
