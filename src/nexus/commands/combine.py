"""
combines a series of nexuses into one nexus.
"""
from nexus.tools import combine_nexuses
from nexus.cli_util import add_nexus, get_reader, add_output, write_output


def register(parser):
    add_output(parser)
    add_nexus(parser, many=True)


def run(args):
    write_output(combine_nexuses(get_reader(args, many=True)), args)
