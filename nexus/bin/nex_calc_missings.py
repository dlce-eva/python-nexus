#!/usr/bin/env python
"""Calculates the number of missing entries in each site in a nexus file"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
import os
from nexus.reader import NexusReader

def count_missings(nexus_obj):
    """
    Counts the number of missing/gap sites in a nexus
    
    """
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    missing = {}
    for taxon, characters in nexus_obj.data:
        missing[taxon] = missing.get(taxon, 0)
        characters = "".join(characters)
        for c in characters:
            if c in ('?', '-'):
                missing[taxon] += 1
    return missing


if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog fudge.nex")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
    except IndexError:
        parser.print_help()
        sys.exit()
        
    nexus = NexusReader(nexusname)
    missings = count_missings(nexus)
    
    print "Missing data in %s" % nexusname
    for taxon in missings:
        print("%s: %d/%d (%0.2f%%)" % \
            (taxon.ljust(20), missings[taxon], nexus.data.nchar, (missings[taxon]/nexus.data.nchar)*100)
        )
    print('-'*76)
    total_missing = sum([x for x in missings.values()])
    total_data = nexus.data.nchar * nexus.data.ntaxa
    print('TOTAL: %d/%d (%0.2f%%)' % \
        (total_missing, total_data, (total_missing/total_data)*100)
    )
