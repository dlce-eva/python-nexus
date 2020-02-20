"""
Converts binary nexuses to a multistate nexus.
"""
import argparse

from nexus.tools import multistatise, combine_nexuses
from nexus.cli_util import add_nexus, get_reader, add_output, write_output


def register(parser):
    parser.add_argument('--charblock', help=argparse.SUPPRESS, action='store_false', default=True)
    parser.add_argument('--interleave', help=argparse.SUPPRESS, action='store_true', default=False)
    add_output(parser)
    add_nexus(parser, many=True)


def run(args):
    nexuslist = [multistatise.multistatise(n) for n in get_reader(args, many=True)]
    write_output(combine_nexuses(nexuslist), args)
