#!/usr/bin/env python
import sys
import os
from nexus import NexusReader, NexusWriter, VERSION
from nexus.tools.binarise import binarise
__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexus_multistate2binary - python-nexus tools v%(version)s

Converts multistate nexuses to binary present/absent form.
""" % {'version': VERSION, }

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog old.nex new.nex")
    options, args = parser.parse_args()

    try:
        nexusname = args[0]
        newnexusname = args[1]
    except IndexError:
        print(__doc__)
        print("Author: %s\n" % __author__)
        parser.print_help()
        sys.exit()
        
    new = binarise(NexusReader(nexusname))
    new.write_to_file(newnexusname)
