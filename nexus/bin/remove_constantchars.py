#!/usr/bin/env python
"""remove_constantchars - python-nexus tools 
Removes the constant characters from a nexus
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
import os

from nexus.reader import NexusReader, NexusFormatException
from nexus.writer import NexusWriter

def find_constant_sites(nexus_obj):
    """
    Returns a list of the constant sites in a nexus
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :return: A list of constant site positions.
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
        
    const = []
    for i in range(0, nexus_obj.data.nchar):
        states = []
        for taxa, data in nexus_obj.data:
            characters = "".join(data)
            c = characters[i]
            if c in ('?', '-'):
                continue
            elif c not in states:
                states.append(c)
        
        if len(states) == 1:
            const.append(i)
    return const
    
def new_nexus_without_sites(nexus_obj, sites_to_remove):
    # make new nexus
    nexout = NexusWriter()
    nexout.add_comment(
        "Removed %d constant sites: %s" %
        (len(sites_to_remove), ",".join(["%s" % s for s in sites_to_remove]))
    )
    new_sitepos = 0
    for sitepos in range(nexus_obj.data.nchar):
        if sitepos in sites_to_remove:
            continue # skip!
        for taxon, data in nexus.data:
            nexout.add(taxon, new_sitepos, data[sitepos])
        new_sitepos += 1
    return nexout
    

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog fudge.nex newfile.nex")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
        newfile = args[1]
    except IndexError:
        print __doc__
        print "Author: %s\n" % __author__
        parser.print_help()
        sys.exit()
        
    nexus = NexusReader(nexusname)
    const = find_constant_sites(nexus)
    print("%d constant sites found: %s" % (len(const), ",".join(["%s" % s for s in const])))
    if len(const) == 0:
        raise Exception("Nothing to do!")
        quit()
    
    new = new_nexus_without_sites(nexus, const)
    new.write_to_file(filename=newfile)
    