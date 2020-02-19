from clldutils.clilib import PathType

from nexus import NexusReader


def add_nexus(parser, many=False):
    kw = {}
    if many:
        kw['nargs'] = '+'
    parser.add_argument(
        "filename",
        help='Path to Nexus file',
        type=PathType(type='file'),
        **kw)


def add_output(parser):
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="output nexus file, if not specified, output will be printed to stdout")


def get_reader(args, many=False):
    if many:
        return [NexusReader.from_file(f) for f in args.filename]
    return NexusReader.from_file(args.filename)


def write_output(writer, args):
    if args.output:
        print('Output written to {0}'.format(writer.write_to_file(args.output, **vars(args))))
    else:
        print(writer.write(**vars(args)))
