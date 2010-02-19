#!/usr/bin/env python
import sys
import os
from nexus import NexusReader, NexusWriter, NexusFormatException, VERSION
__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexus_multistate2binary - python-nexus tools v%(version)s

Converts multistate nexuses to binary present/absent form.
""" % {'version': VERSION,}


def binarise(nexus_obj, one_nexus_per_block=False):
    """
    Returns a binary variant of the given `nexus_obj`.
    If `one_nexus_per_block` then we return a list of NexusWriter instances.
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :param one_nexus_per_block: Whether to return a single NexusWriter, or a 
                                list of NexusWriter's (one per character)
    :type one_nexus_per_block: Boolean
    
    :return: A NexusWriter instance or a list of NexusWriter instances.
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
    
    nexuslist = []
    n = NexusWriter()
    for site, data in nexus_obj.data.characters.items():
        for taxon, state in data.items():
            n.add(taxon, site, state)
            
        if one_nexus_per_block:
            n.recode_to_binary()
            nexuslist.append(n)
            n = NexusWriter()
            
    if one_nexus_per_block:
        return nexuslist
    else:
        n.recode_to_binary()
        return n

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog old.nex new.nex")
    parser.add_option("-1", "--onefile", dest="onefile", 
            action="store_true", default=False, 
            help="One nexus file for each multistate character")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
        newnexusname = args[1]
    except IndexError:
        print __doc__
        print "Author: %s\n" % __author__
        parser.print_help()
        sys.exit()
        
    nexus = NexusReader(nexusname)
    
    new = binarise(nexus, one_nexus_per_block=options.onefile)
    if isinstance(new, NexusWriter):
        new.write_to_file(newnexusname)
    elif len(new) > 1:
        newnexusname, ext = os.path.splitext(newnexusname)
        for nex in new:
            nex.write_to_file("%s-%s%s" % (newnexusname, nex.clean(nex.characters[0]), ext))
            
    
