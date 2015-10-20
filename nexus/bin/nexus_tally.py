#!/usr/bin/env python
from __future__ import print_function
from textwrap import TextWrapper
from nexus import NexusReader, VERSION
from nexus.tools import tally_by_taxon, tally_by_site, count_binary_set_size

__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexusmanip - python-nexus tools v%(version)s

Performs a number of nexus counting/tallying methods.
""" % {'version': VERSION, }

def print_tally(tally):
    wrapper = TextWrapper(initial_indent=" ", subsequent_indent="\t", width=65)
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

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [taxa/sites/binary] nexus.nex")
    options, commands = parser.parse_args()

    if len(commands) != 2:
        print(__doc__)
        print("Author: %s\n" % __author__)
        parser.print_help()
        quit()

    command, nex = commands

    try:
        nex = NexusReader(nex)
    except IOError:
        raise IOError("Unable to read %s" % nex)

    if command in ('taxa', 't'):
        print_tally(tally_by_taxon(nex))
    elif command in ('site', 's'):
        print_tally(tally_by_site(nex))
    elif command in ('binary', 'b'):
        print_binary(count_binary_set_size(nex))
    else:
        quit("Invalid tally command. Only 'taxa' and 'site' are valid.")
