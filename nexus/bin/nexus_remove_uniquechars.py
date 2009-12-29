#!/usr/bin/env python
"""remove_uniquechars - python-nexus tools 
Removes the unique characters from a nexus 
(i.e. sites with only one taxon belonging to them - this only really makes sense
if the data is coded as presence/absence in binary format)
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import sys
import os

from nexus import NexusReader, NexusWriter, NexusFormatException
from nexus_remove_constantchars import new_nexus_without_sites

def find_unique_sites(nexus_obj):
    """
    Returns a list of the unique sites in a binary nexus
    i.e. sites with only one taxon belonging to them.
        (this only really makes sense if the data is coded as presence/absence)
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :return: A list of unique site positions.
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
    
    unique = []
    for i in range(0, nexus_obj.data.nchar):
        members = {}
        missing = 0
        for taxa, characters in nexus_obj.data:
            c = characters[i]
            if c in (u'?', u'-'):
                missing += 1
            else:
                members[c] = members.get(c, 0) + 1
        
        # a character is unique if there's only two states
        # AND there's a state with 1 member 
        # AND the state with 1 member is NOT the 0 (absence) state
        print i, missing, members
        if len(members) == 2:
            for state, count in members.items():
                if state != '0' and count == 1:
                    unique.append(i)
    print unique
    return unique
    

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
    const = find_unique_sites(nexus)
    print("%d unique sites found: %s" % (len(const), ",".join(["%s" % s for s in const])))
    if len(const) == 0:
        raise Exception("Nothing to do!")
        quit()
    
    new = new_nexus_without_sites(nexus, const)
    new.write_to_file(filename=newfile)
    