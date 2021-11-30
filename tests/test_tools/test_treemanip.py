"""Tests for utils in bin directory"""
import pytest

from nexus.tools import (
    delete_trees, sample_trees, strip_comments_in_trees, visit_tree_nodes, visit_trees)


def test_decorator_order(trees, tmp_path):
    tmp_path.joinpath('t.nex').write_text(trees.write(), encoding='utf8')
    new_nex = delete_trees(trees.write(), [2])
    assert len(new_nex.trees.trees) == 2
    new_nex = delete_trees(tmp_path / 't.nex', [2])
    assert len(new_nex.trees.trees) == 2


def test_visit_tree_nodes(trees):
    def rename(n):
        n.name = n.name.lower() if n.name else n.name
    assert 'chris' not in trees.write()
    res = visit_tree_nodes(trees.write(), rename)
    assert 'chris' in res.write()


def test_visit_trees(trees):
    def prune_chris(tree):
        tree.prune_by_names(['Chris'])
        return tree
    assert 'Chris' in trees.write()
    res = visit_trees(trees.write(), prune_chris)
    print(res.trees.trees)
    assert 'Chris' not in res.write()
    leafs = res.trees.trees[0].newick_tree.get_leaf_names()
    assert 'Bruce' in leafs and ('Chris' not in leafs)


def test_run_deltree(trees):
    new_nex = delete_trees(trees, [2])
    assert len(new_nex.trees.trees) == 2
    assert new_nex.trees.ntrees == 2
    assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
    assert new_nex.trees[1].startswith('tree tree.20000.883.396049')


def test_run_resample_1(trees):
    # shouldn't resample anything..
    new_nex = sample_trees(trees, every_nth=1)
    assert len(new_nex.trees.trees) == 3
    assert new_nex.trees.ntrees == 3
    assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
    assert new_nex.trees[1].startswith('tree tree.10000.874.808756')
    assert new_nex.trees[2].startswith('tree tree.20000.883.396049')


def test_run_removecomments(trees_beast):
    new_nex = strip_comments_in_trees(trees_beast)
    assert '[&lnP=-15795.47019648783]' not in new_nex.trees[0]


def test_run_randomise_sample1(trees_translated):
    new_nex = sample_trees(trees_translated, 1)
    assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 1


def test_run_randomise_sample2(trees_translated):
    new_nex = sample_trees(trees_translated, 2)
    assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 2


def test_run_randomise_sample_toobig(trees_translated):
    # raises ValueError, sample size too big (only 3 trees in this file)
    with pytest.raises(ValueError):
        sample_trees(trees_translated, 10)
