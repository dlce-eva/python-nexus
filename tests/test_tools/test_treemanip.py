"""Tests for utils in bin directory"""
import pytest

from nexus.bin.nexus_treemanip import parse_deltree, run_deltree
from nexus.bin.nexus_treemanip import run_random
from nexus.bin.nexus_treemanip import run_removecomments
from nexus.bin.nexus_treemanip import run_resample
from nexus.bin.nexus_treemanip import run_detranslate


def test_simple():
    assert parse_deltree('1') == [1]
    assert parse_deltree('1,2,3') == [1, 2, 3]
    assert parse_deltree('1,3,5') == [1, 3, 5]
    assert parse_deltree('1-10') == \
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert parse_deltree('1,3,4-6') == \
        [1, 3, 4, 5, 6]
    assert parse_deltree('1,3,4-6,8,9-10') == \
        [1, 3, 4, 5, 6, 8, 9, 10]

def test_alternate_range():
    assert parse_deltree('1:10') == \
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert parse_deltree('1,3,4:6') == \
        [1, 3, 4, 5, 6]
    assert parse_deltree('1,3,4:6,8,9:10') == \
        [1, 3, 4, 5, 6, 8, 9, 10]

def test_error():
    with pytest.raises(ValueError):
        parse_deltree("1-x")
    with pytest.raises(ValueError):
        parse_deltree("sausage")
    with pytest.raises(ValueError):
        parse_deltree("first:last")


def test_run_deltree(trees):
    new_nex = run_deltree('2', trees, do_print=False)
    assert len(new_nex.trees.trees) == 2
    assert new_nex.trees.ntrees == 2
    assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
    assert new_nex.trees[1].startswith('tree tree.20000.883.396049')
    

def test_run_resample_1(trees):
    # shouldn't resample anything..
    new_nex = run_resample('1', trees, do_print=False)
    assert len(new_nex.trees.trees) == 3
    assert new_nex.trees.ntrees == 3
    assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
    assert new_nex.trees[1].startswith('tree tree.10000.874.808756')
    assert new_nex.trees[2].startswith('tree tree.20000.883.396049')


def test_run_removecomments(trees_beast):
    new_nex = run_removecomments(trees_beast, do_print=False)
    assert '[&lnP=-15795.47019648783]' not in new_nex.trees[0]


def test_failure_on_nonint(trees_translated):
    with pytest.raises(ValueError):
        run_random('fudge', trees_translated)


def test_run_randomise_sample1(trees_translated):
    new_nex = run_random(1, trees_translated)
    assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 1


def test_run_randomise_sample2(trees_translated):
    new_nex = run_random(2, trees_translated)
    assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 2


def test_run_randomise_sample_toobig(trees_translated):
    # raises ValueError, sample size too big (only 3 trees in this file)
    with pytest.raises(ValueError):
        run_random(10, trees_translated)
        

def test_run_detranslate(trees_translated, trees):
    assert not trees_translated.trees._been_detranslated
    nex = run_detranslate(trees_translated)
    # should NOW be the same as tree 0 in example.trees
    assert trees.trees[0] == nex.trees[0]
