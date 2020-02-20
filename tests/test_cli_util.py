import io
import argparse

import pytest
from clldutils.clilib import ParserError

from nexus.cli_util import list_of_ranges, get_reader


def test_get_reader(monkeypatch):
    monkeypatch.setattr('sys.stdin', io.StringIO('#NEXUS\n\nbegin trees;\ntree t = ();\nend;'))
    with pytest.raises(ParserError):
        get_reader(argparse.Namespace(filename=None), required_blocks=['data'])


@pytest.mark.parametrize(
    'in_,out_',
    [
        ('1', [1]),
        ('1,2,3', [1, 2, 3]),
        ('1,3,5', [1, 3, 5]),
        ('1-10', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ('1,3,4-6', [1, 3, 4, 5, 6]),
        ('1,3,4-6,8,9-10', [1, 3, 4, 5, 6, 8, 9, 10]),
        ('1:10', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ('1,3,4:6', [1, 3, 4, 5, 6]),
        ('1,3,4:6,8,9:10', [1, 3, 4, 5, 6, 8, 9, 10]),
    ]
)
def test_list_of_ranges(in_, out_):
    assert list_of_ranges(in_) == out_


@pytest.mark.parametrize(
    'in_',
    ['1-x', 'sausage', 'first:last']
)
def test_error(in_):
    with pytest.raises(argparse.ArgumentTypeError):
        list_of_ranges(in_)
