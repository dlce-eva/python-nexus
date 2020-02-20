"""
Performs a number of nexus counting/tallying methods.
"""
import textwrap
import _collections

from nexus.cli_util import add_nexus, get_reader
from nexus.tools import tally_by_taxon, tally_by_site, count_binary_set_size

TALLY_TYPES = _collections.OrderedDict([
    ('taxa', tally_by_taxon),
    ('site', tally_by_site),
    ('binary', count_binary_set_size),
])


def register(parser):
    add_nexus(parser)
    parser.add_argument(
        '-t', '--type',
        help='Typeof tally to compute',
        choices=list(TALLY_TYPES.keys()),
        default=list(TALLY_TYPES.keys())[0]
    )


def run(args):
    printer = print_binary if args.type == 'binary' else print_tally
    printer(TALLY_TYPES[args.type](get_reader(args)))


def print_tally(tally):
    wrapper = textwrap.TextWrapper(initial_indent=" ", subsequent_indent="\t", width=65)
    for tkey in sorted(tally):
        print(tkey)
        for skey in sorted(tally[tkey]):
            s = " ".join(sorted(["%s" % v for v in tally[tkey][skey]]))
            print(" - %s: " % skey, end="")
            for w in wrapper.wrap(s):
                print(w)
        print("\n")
    return


def print_binary(tally):
    for i in sorted(tally):
        print("%d\t%d" % (i, tally[i]))
    return
