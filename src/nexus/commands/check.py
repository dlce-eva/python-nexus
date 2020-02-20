"""
Check nexus files for errors
"""
import warnings

from nexus.cli_util import add_nexus, get_reader
from nexus.checker import CHECKERS


def register(parser):
    add_nexus(parser)
    parser.add_argument(
        '-e', "--extra",
        help="add extra checks",
        action='store_true'
    )
    parser.add_argument(
        '-a', "--ascertainment",
        help="add ascertainment checks",
        action='store_true'
    )


def run(args):
    checkers = CHECKERS['base']
    if args.extra:
        checkers.extend(CHECKERS['extra'])
    if args.ascertainment:
        checkers.extend(CHECKERS['ascertainment'])

    with warnings.catch_warnings(record=True) as warned:
        warnings.simplefilter("always")
        nex = get_reader(args)

        if len(warned):
            print("Warnings encountered in reading nexus:")
            for w in warned:
                print("\t%s" % w)

    for checker in checkers:
        checker(nex).status()
