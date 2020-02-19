import os

import pytest

from nexus import NexusReader
from nexus.exceptions import NexusFormatException
from nexus.tools.check_for_valid_NexusReader import check_for_valid_NexusReader


def test_valid_NexusReader():
    check_for_valid_NexusReader(NexusReader())

def test_failure_on_nonnexus_1():
    with pytest.raises(TypeError):
        check_for_valid_NexusReader('none')


def test_failure_on_nonnexus_2():
    with pytest.raises(TypeError):
        check_for_valid_NexusReader(1)


def test_failure_on_nonnexus_3():
    with pytest.raises(TypeError):
        check_for_valid_NexusReader([1, 2, 3])


def test_failure_on_required_block_one(make_reader):
    nexus_obj = make_reader('example.nex')
    with pytest.raises(NexusFormatException):
        check_for_valid_NexusReader(nexus_obj, ['trees'])


def test_failure_on_required_block_two(make_reader):
    nexus_obj = make_reader('example2.nex')
    with pytest.raises(NexusFormatException):
        check_for_valid_NexusReader(nexus_obj, ['r8s'])


def test_valid_with_required_block_one(make_reader):
    nexus_obj = make_reader('example.nex')
    check_for_valid_NexusReader(nexus_obj, ['data'])


def test_valid_with_required_block_two(make_reader):
    nexus_obj = make_reader('example2.nex')
    check_for_valid_NexusReader(nexus_obj, ['data', 'taxa'])
