#!/usr/bin/env python
import sys
import os
from nexus import NexusReader, NexusFormatException, VERSION
__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexusmanip - python-nexus tools v%(version)s

Performs a number of nexus manipulation methods.
""" % {'version': VERSION,}


def count_missings(nexus_obj):
    """
    Counts the number of missing/gap sites in a nexus
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :return: A dictionary of taxa and missing counts
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
    
    missing = {}
    for taxon, characters in nexus_obj.data:
        missing[taxon] = missing.get(taxon, 0)
        characters = "".join(characters)
        for c in characters:
            if c in ('?', '-'):
                missing[taxon] += 1
    return missing

def print_missing_characters(nexuss_obj):
    """
    Counts the number of missing/gap sites in a nexus.
    
    (Wrapper around `count_missings`)
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    """
    missings = count_missings(nexus)
    
    print ("Missing data in %s" % nexusname)
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


if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog old.nex [new.nex]")
    parser.add_option("-m", "--missings", dest="missings", 
            action="store", default=False, 
            help="Count the missing characters")
    # parser.add_option("-r", "--resample", dest="resample", 
    #         action="store", default=False, 
    #         help="Resample the trees every Nth tree")
    
    try:
        nexusname = args[0]
    except IndexError:
        print __doc__
        print "Author: %s\n" % __author__
        parser.print_help()
        sys.exit()
        
    try:
        newnexus = args[1]
    except IndexError:
        newnexus = None
        
    
    nexus = NexusReader(nexusname)
    
    if options.missings:
        print_missing_characters(nexus)
    
    
