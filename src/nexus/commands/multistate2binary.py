"""
Converts a multistate nexus file to binary present/absent form.
"""
from nexus.tools.binarise import binarise
from nexus.cli_util import add_nexus, get_reader, add_output, write_output


def register(parser):
    add_output(parser)
    add_nexus(parser)


def run(args):
    write_output(binarise(get_reader(args)), args)
