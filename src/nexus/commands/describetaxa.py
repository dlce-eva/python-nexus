"""
Displays some simple nexus info
"""
import collections

from clldutils.clilib import Table, add_format

from nexus.cli_util import add_nexus, get_reader


def register(parser):
    add_nexus(parser)
    add_format(parser, default='simple')


def run(args):
    nexus_obj = get_reader(args, required_blocks=['data'])
    print(nexus_obj.filename)

    with Table(args, 'Taxon', 'Characters') as t:
        for taxon in sorted(nexus_obj.data.matrix):
            tally = collections.Counter()
            for site in nexus_obj.data.matrix[taxon]:
                tally.update([site])

            t.append([taxon, ", ".join(['%s x %s' % (k, tally[k]) for k in sorted(tally)])])
