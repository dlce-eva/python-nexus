#!/usr/bin/env python
import sys
import os
from nexus import NexusReader, NexusWriter, NexusFormatException, VERSION
from nexus.tools import multistatise, combine_nexuses
__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexus_binary2multistate - python-nexus tools v%(version)s

Converts binary nexuses to a multistate nexus.
""" % {'version': VERSION,}

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog nex1.nex nex2.nex ... nexN.nex")
    options, nexuslist = parser.parse_args()

    if len(nexuslist) <= 1:
        print __doc__
        parser.print_help()
        sys.exit()
    
    nexuslist2 = []
    for nfile in nexuslist:
        n = NexusReader(nfile)
        n = multistatise(n)
        nexuslist2.append(n)
        
    out = combine_nexuses(nexuslist2)
    out.write_to_file('multistate.nex', charblock=True, interleave=False)
    print("Written to multistate.nex")