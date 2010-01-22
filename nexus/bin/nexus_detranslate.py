#!/usr/bin/env python
import sys
import os
from nexus import NexusReader, VERSION

__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """detranslate - python-nexus tools v%(version)s
Converts an nexus tree file with 'translated' taxa labels to a detranslated form
""" % {'version': VERSION,}

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog fudge.nex output.nex")
    parser.add_option("-r", "--removecomments", dest="removecomments", 
            action="store_true", default=False, 
            help="Remove comments inside the tree definition")
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
    if 'trees' not in nexus.blocks:
        sys.exit("No trees found in file %s!" % nexusname)
    if nexus.trees.ntrees == 0:
        sys.exit("No trees found in found %s!" % nexusname)
    if nexus.trees.was_translated == False:
        sys.exit("Trees in %s do not appear to be translated!" % nexusname)
    print "%d trees found with %d translated taxa" % \
        (nexus.trees.ntrees, len(nexus.trees.translators))
        
        
    if options.removecomments:
        print "Removing comments..."
        new = []
        for tree in nexus.trees:
            new.append(nexus.trees.remove_comments(tree))
        nexus.trees.trees = new
    nexus.write_to_file(newnexus)
    
    
    print "New nexus written to %s" % newnexus