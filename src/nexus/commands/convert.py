"""
Convert a nexus file to a different format
"""
import textwrap

from nexus.cli_util import add_nexus, get_reader, add_output, write_output
from nexus.util import FileWriterMixin


def register(parser):
    add_nexus(parser)
    add_output(parser)
    parser.add_argument('--format', choices=['fasta'], default='fasta', help='Output format')


def run(args):
    write_output(Converter(get_reader(args)), args)


class Converter(FileWriterMixin):
    def __init__(self, nex):
        self.nex = nex

    def write(self, format='fasta', **kw):
        res = []
        if format == 'fasta':
            for taxon in sorted(self.nex.data.matrix):
                res.append('>%s' % taxon)
                for line in textwrap.wrap("".join(self.nex.data.matrix[taxon]), 70):
                    res.append(line)
        else:  # pragma: no cover
            raise NotImplementedError(format)

        return '\n'.join(res)
