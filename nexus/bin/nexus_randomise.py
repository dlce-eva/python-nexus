#!/usr/bin/env python
"""randomise - python-nexus tools 
Shuffles the characters between each taxon to create a new nexus
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
import os
from random import shuffle, randrange

from nexus import NexusReader, NexusWriter

def shufflenexus(nexus_obj, resample=False):
    """
    Shuffles the characters between each taxon to create a new nexus
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :param resample: The number of characters to resample. If set to False, then
        the number of characters will equal the number of characters in the 
        original data file.
    :type resample: Integer
    
    :return: A shuffled NexusReader instance
    :raises AssertionError: if nexus_obj is not a nexus
    :raises ValueError: if resample is not False or a positive Integer
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
    
    if resample is False:
        resample = nexus_obj.data.nchar
    
    try:
        resample = int(resample)
    except ValueError:
        raise ValueError('resample must be a positive integer or False!')
    
    if resample < 1:
        raise ValueError('resample must be a positive integer or False!')
    
    newnexus = NexusWriter()
    newnexus.add_comment("Randomised Nexus generated from %s" % nexus_obj.filename)
    
    for i in range(resample):
        # pick existing character
        character = randrange(0, nexus_obj.data.nchar)
        chars = nexus_obj.data.characters[character]
        site_values = [chars[taxon] for taxon in nexus_obj.data.taxa]
        shuffle(site_values)
        for taxon in nexus_obj.data.taxa:
            newnexus.add(taxon, i, site_values.pop(0))
    return newnexus
    
    

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog -n 100 fudge.nex output.nex")
    parser.add_option("-n", "--numchars", dest="numchars", 
            action="store", default=False, 
            help="Number of Characters to Generate")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
        newnexus = args[1]
    except IndexError:
        print __doc__
        print "Author: %s\n" % __author__
        parser.print_help()
        sys.exit()
        
    if options.numchars != False:
        try:
            options.numchars = int(options.numchars)
        except ValueError:
            print "numchars needs to be a number!"
            raise
        
    nexus = NexusReader(nexusname)
    nexus = shufflenexus(nexus, options.numchars)
    nexus.write_to_file(newnexus)
    print "New random nexus written to %s" % newnexus