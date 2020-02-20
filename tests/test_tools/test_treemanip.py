"""Tests for utils in bin directory"""
import pytest

from nexus.commands.trees import run_deltree
from nexus.commands.trees import run_random
from nexus.commands.trees import run_removecomments
from nexus.commands.trees import run_resample


def test_run_deltree(trees, mocker):
    new_nex = run_deltree([2], trees, mocker.Mock())
    assert len(new_nex.trees.trees) == 2
    assert new_nex.trees.ntrees == 2
    assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
    assert new_nex.trees[1].startswith('tree tree.20000.883.396049')


def test_run_resample_1(trees, mocker):
    # shouldn't resample anything..
    new_nex = run_resample(1, trees, mocker.Mock())
    assert len(new_nex.trees.trees) == 3
    assert new_nex.trees.ntrees == 3
    assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
    assert new_nex.trees[1].startswith('tree tree.10000.874.808756')
    assert new_nex.trees[2].startswith('tree tree.20000.883.396049')


def test_run_removecomments(trees_beast, mocker):
    new_nex = run_removecomments(trees_beast, mocker.Mock())
    assert '[&lnP=-15795.47019648783]' not in new_nex.trees[0]


def test_run_randomise_sample1(trees_translated, mocker):
    new_nex = run_random(1, trees_translated, mocker.Mock())
    assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 1


def test_run_randomise_sample2(trees_translated, mocker):
    new_nex = run_random(2, trees_translated, mocker.Mock())
    assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 2


def test_run_randomise_sample_toobig(trees_translated, mocker):
    # raises ValueError, sample size too big (only 3 trees in this file)
    with pytest.raises(ValueError):
        run_random(10, trees_translated, mocker.Mock())
