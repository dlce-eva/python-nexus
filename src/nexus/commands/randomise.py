"""
Shuffles the characters between each taxon to create a new nexus
"""
from nexus.tools import shufflenexus
from nexus.cli_util import add_nexus, get_reader, add_output, write_output


def register(parser):
    add_nexus(parser)
    add_output(parser)
    parser.add_argument(
        "-n", "--numchars",
        default=0,
        type=int,
        help="Number of Characters to Generate")


def run(args):
    write_output(shufflenexus(get_reader(args), args.numchars or False), args)
