#!/usr/bin/env python
"""Displays some simple nexus info"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
from nexus import NexusReader


if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog nexusname")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
    except IndexError:
        parser.print_help()
        sys.exit()
    
    n = NexusReader(nexusname)
    print n
    for k, v in n.blocks.items():
        print ' ', k, v
        
