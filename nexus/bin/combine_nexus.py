#!/usr/bin/env python
"""combine-nexus - python-nexus tools 
combines a series of nexuses into one nexus.
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
import os
from nexus import NexusReader, NexusWriter, NexusFormatException

def combine_nexuses(nexuslist):
    """
    Combines a list of NexusReader instances into a single nexus
    
    :param nexuslist: A list of NexusReader instances
    :type nexuslist: List 
    
    :return: A NexusWriter instance
    
    :raises TypeError: if nexuslist is not a list of NexusReader instances
    :raises IOError: if unable to read an file in nexuslist
    :raises NexusFormatException: if a nexus file does not have a `data` block
    """
    if isinstance(nexuslist, list) == False:
        raise TypeError("nexuslist is not a list")
    
    out = NexusWriter()
    charpos = 1
    for nex in nexuslist:
        if isinstance(nex, NexusReader) == False:
            raise TypeError("%s is not a NexusReader instance" % nex)
        
        if 'data' not in nex.blocks:
            raise NexusFormatException("Warning: %s has no data block" % nex.filename)
        
        out.add_comment("%d - %d: %s" % (charpos, charpos + nex.data.nchar -1, nex.filename))
        
        for site, data in nex.data.characters.items():
            charpos += site
            for taxon, value in data.items():
                out.add(taxon, charpos, value)
        charpos += 1
    return out
    

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog nex1.nex nex2.nex ... nexN.nex")
    options, nexuslist = parser.parse_args()
    
    if len(nexuslist) <= 1:
        parser.print_help()
        sys.exit()
    
    nexuslist = [NexusReader(n) for n in nexuslist]
    out = combine_nexuses(nexuslist)
    out.write_to_file('combined.nex', charblock=False, interleave=False)
    print("Written to combined.nex")