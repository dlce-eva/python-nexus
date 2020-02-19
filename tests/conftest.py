import pathlib

import pytest

from nexus import NexusReader


@pytest.fixture
def regression():
    return pathlib.Path(__file__).parent / 'regression'


@pytest.fixture
def examples():
    return pathlib.Path(__file__).parent / 'examples'


@pytest.fixture
def make_reader(examples):
    def _make(fname):
        return NexusReader(examples / fname)
    return _make


@pytest.fixture
def nex(make_reader):
    return make_reader('example.nex')


@pytest.fixture
def nex2(make_reader):
    return make_reader('example2.nex')


@pytest.fixture
def nex3(make_reader):
    return make_reader('example3.nex')


@pytest.fixture
def nexc(make_reader):
    return make_reader('example-characters.nex')


@pytest.fixture
def trees(make_reader):
    return make_reader('example.trees')


@pytest.fixture
def trees_translated(make_reader):
    return make_reader('example-translated.trees')


@pytest.fixture
def trees_beast(make_reader):
    return make_reader('example-beast.trees')
