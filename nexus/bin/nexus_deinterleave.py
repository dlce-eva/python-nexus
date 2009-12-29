#!/usr/bin/env python
"""deinterleave - python-nexus tools 
Converts an interleaved nexus to a simple nexus.
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
import os
from nexus import NexusReader, NexusFormatException

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog fudge.nex output.nex")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
        newnexus = args[1]
    except IndexError:
        print __doc__
        print "Author: %s\n" % __author__
        parser.print_help()
        sys.exit()
        
    nexus = NexusReader(nexusname)
    nexus.write_to_file(newnexus)
    print "New nexus written to %s" % newnexus