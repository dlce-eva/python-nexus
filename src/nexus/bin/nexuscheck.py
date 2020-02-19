#!/usr/bin/env python
import warnings
from __future__ import print_function
from nexus import NexusReader, VERSION
from nexus.checker import checkers

__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexusmanip - python-nexus tools v%(version)s

Checks nexus files for errors.
""" % {'version': VERSION, }

from nexus.checker import CHECKERS


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Checks nexus files for errors')
    parser.add_argument("filename", help='filename')
    parser.add_argument(
        '-e', "--extra", dest='extra',
        help="add extra checks", action='store_true'
    )
    parser.add_argument(
        '-a', "--ascertainment", dest='ascertainment',
        help="add ascertainment checks", action='store_true'
    )
    parser.add_argument(
        '-v', "--verbose", dest='verbose',
        help="more output", action='store_true'
    )
    args = parser.parse_args()
    
    checkers = CHECKERS['base']
    if args.extra:
        checkers.extend(CHECKERS['extra'])
    if args.ascertainment:
        checkers.extend(CHECKERS['ascertainment'])
    
    with warnings.catch_warnings(record=True) as warned:
        warnings.simplefilter("always")
        nex = NexusReader(args.filename)
        
        if len(warned):
            print("Warnings encountered in reading nexus:")
            for w in warned:
                print("\t%s" % w)
    
    for checker in checkers:
        checker(nex, verbose=args.verbose).status()
