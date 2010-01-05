#!/usr/bin/env python
import sys
import os
from nexus import NexusReader, VERSION

__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """treemanip.py - python-nexus tools v%(version)s
Performs some functions on trees
""" % {'version': VERSION,}

__usage__ = """
Deleting trees:
    nexus_treemanip.py -d 1 fudge.trees output.nex   - delete tree #1
    nexus_treemanip.py -d 1-5 fudge.trees output.nex - delete trees #1-5
    nexus_treemanip.py -d 1,4 fudge.trees output.nex - delete trees #1 and #5
    nexus_treemanip.py -d 1,4,20-30 fudge.trees output.nex - delete trees #1, #4, and #20-30

"""

class TreeListException(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)
        self.arg = arg

def parse_deltree(dstring):
    """
    Returns a list of trees to be deleted
    
    >>> parse_deltree('1')
    [1]
    >>> parse_deltree('1,2,3')
    [1, 2, 3]
    >>> parse_deltree('1,3,5')
    [1, 3, 5]
    >>> parse_deltree('1-10')
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> parse_deltree('1,3,4-6')
    [1, 3, 4, 5, 6]
    >>> parse_deltree('1,3,4-6,8,9-10')
    [1, 3, 4, 5, 6, 8, 9, 10]
    """
    out = []
    for token in dstring.split(','):
        if '-' in token:
            try:
                start, stop = token.split("-")
                out.extend([x for x in range(int(start), int(stop)+1)])
            except (ValueError, IndexError):
                raise TreeListException("'%s' is not a valid token for a tree list" % token)
        else:
            try:
                out.append(int(token))
            except (ValueError):
                raise TreeListException("'%s' is not a valid token for a tree list" % token)
    return sorted(out)
    

if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog fudge.trees output.nex")
    parser.add_option("-d", "--deltree", dest="deltree", 
            action="store", default=False, 
            help="Remove the listed trees")
    parser.add_option("-r", "--resample", dest="resample", 
            action="store", default=False, 
            help="Resample the trees every Nth tree")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
        newnexus = args[1]
    except IndexError:
        print __doc__
        print __usage__
        print "Author: %s\n" % __author__
        parser.print_help()
        sys.exit()
        
    nexus = NexusReader(nexusname)
    if 'trees' not in nexus.blocks:
        sys.exit("No trees found in file %s!" % nexusname)
    if nexus.trees.ntrees == 0:
        sys.exit("No trees found in found %s!" % nexusname)
    print "%d trees found with %d translated taxa" % \
        (nexus.trees.ntrees, len(nexus.trees.translators))
    
    # Delete trees
    if options.deltree:
        new = []
        delitems = parse_deltree(options.deltree)
        print 'Deleting: %d trees' % len(delitems)
        for index, tree in enumerate(nexus.trees, 1):
            if index in delitems:
                print 'Deleting tree %d' % index
            else:
                new.append(tree)
        nexus.trees.trees = new
    
    # Resample trees
    elif options.resample:
        new = []
        try:
            every = int(options.resample)
        except ValueError:
            sys.exit("Invalid resample option %s - should be an integer" % options.resample)
        
        ignore_count = 0 
        for index, tree in enumerate(nexus.trees, 1):
            if index % every == 0:
                new.append(tree)
            else:
                ignore_count += 1
        print "Ignored %d trees" % ignore_count
        nexus.trees.trees = new
        
    else:
        sys.exit("No Action Chosen!")
    
    nexus.write_to_file(newnexus)
    print "New nexus written to %s" % newnexus