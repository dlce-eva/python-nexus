#!/usr/bin/env python
"""randomise - python-nexus tools 
Shuffles the characters between each taxon to create a new nexus
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
import os
from random import shuffle

from nexus import NexusReader, NexusWriter

def shufflenexus(nexus_obj):
    """
    Shuffles the characters between each taxon to create a new nexus
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :return: A shuffled NexusReader instance
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
    
    newnexus = NexusWriter()
    newnexus.add_comment("Randomised Nexus generated from %s" % nexus_obj.filename)
    for character in range(nexus_obj.data.nchar):
        chars = nexus_obj.data.characters[character]
        site_values = [chars[taxon] for taxon in nexus_obj.data.taxa]
        shuffle(site_values)
        for taxon in nexus_obj.data.taxa:
            newnexus.add(taxon, character, site_values.pop(0))
    return newnexus
    
    

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
    nexus = shufflenexus(nexus)
    nexus.write_to_file(newnexus)
    print "New random nexus written to %s" % newnexus