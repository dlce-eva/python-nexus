"""
Converts an interleaved nexus to a simple nexus.

See http://mrbayes.sourceforge.net/Help/matrix.html
"""
from nexus.cli_util import add_nexus, get_reader, add_output, write_output


def register(parser):
    add_output(parser)
    add_nexus(parser)


def run(args):
    write_output(get_reader(args), args)
