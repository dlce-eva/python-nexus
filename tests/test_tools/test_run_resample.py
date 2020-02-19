"""Tests for utils in bin directory"""
import pytest

from nexus.bin.nexus_treemanip import run_resample


def test_resample(trees):
    newnex = run_resample(2, trees)
    assert len(newnex.trees.trees) == 1


def test_resample_one(trees):
    newnex = run_resample(1, trees)
    assert len(newnex.trees.trees) == 3


def test_raises_error_on_invalid_resample_value(trees):
    with pytest.raises(ValueError):
        run_resample('a', trees)
    with pytest.raises(ValueError):
        run_resample(None, trees)
    with pytest.raises(ValueError):
        run_resample([], trees)
