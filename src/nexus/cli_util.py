import sys
import argparse

from termcolor import colored
from clldutils.clilib import PathType, ParserError

from nexus import NexusReader


def list_of_ranges(dstring):
    """
    Converts a comma-separated list of 1-based ranges into a list of 1-based indices.

    :param dstring: A string

    :return: `list` of zero-based indices
    """
    def _int(v):
        try:
            return int(v)
        except ValueError:
            raise argparse.ArgumentTypeError("%r is not an integer" % v)

    out = []
    for token in dstring.split(','):
        token = token.replace(':', '-')
        if '-' in token:
            start, stop = token.split("-")
            out.extend([x for x in range(_int(start), _int(stop) + 1)])
        else:
            out.append(_int(token))
    return sorted(out)


def path_or_stdin(string):
    return None if string == '-' else PathType(type='file')(string)


def add_nexus(parser, many=False):
    kw = {}
    if many:
        kw['nargs'] = '+'
    parser.add_argument(
        "filename",
        help='Path to Nexus file, or "-" to read from stdin',
        type=path_or_stdin,
        **kw)


def add_output(parser):
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="output nexus file, if not specified, output will be printed to stdout. "
             "To prevent log messages messing up the output, set '--log-level=WARN'.")


def get_reader(args, many=False, required_blocks=None):
    res = []
    for f in (args.filename if many else [args.filename]):
        if f is None:
            res.append(NexusReader.from_string(sys.stdin.read()))
        else:
            res.append(NexusReader.from_file(f))
    if required_blocks:
        for nex in res:
            for block in required_blocks:
                if not getattr(nex, block, None):
                    raise ParserError(colored(
                        'Nexus file {0} has no {1} block'.format(nex.filename, block),
                        'red',
                        attrs=['bold'],
                    ))
    return res if many else res[0]


def write_output(writer, args):
    if args.output:
        writer.write_to_file(args.output)
        print('Output written to {0}'.format(args.output))
    else:
        print(writer.write())
