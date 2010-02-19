#!/usr/bin/env python
import sys
import os
from nexus import NexusReader, NexusWriter, NexusFormatException, VERSION
__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexusmanip - python-nexus tools v%(version)s

Performs a number of nexus manipulation methods.
""" % {'version': VERSION,}

def count_missing_sites(nexus_obj):
    """
    Counts the number of missing/gap sites in a nexus
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :return: (A dictionary of taxa and missing counts, and a list of log comments)
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

def print_missing_sites(nexus_obj, action, value_dict):
    """
    Prints out counts of the number of missing/gap sites in a nexus.

    (Wrapper around `count_missings`)

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    """
    missings = count_missing_sites(nexus_obj)
    print ("Missing data in %s" % nexus_obj.filename)
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
            c = data[i]
            if c in ('?', '-'):
                continue
            elif c not in states:
                states.append(c)
            
        if len(states) == 1:
            const.append(i)
    return const


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
        if len(members) == 2:
            for state, count in members.items():
                if state != '0' and count == 1:
                    unique.append(i)
    return unique


def print_character_stats(nexus_obj):
    """
    Prints the number of states and members for each site in `nexus_obj`
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :return: A list of the state distribution
    """
    state_distrib = []
    for i in range(0, nexus_obj.data.nchar):
        tally = {}
        for taxa, characters in nexus_obj.data:
            c = characters[i]
            tally[c] = tally.get(c, 0) + 1
        
        print "%5d" % i,
        for state in tally:
            print "%sx%d" % (state, tally[state]),
            state_distrib.append(tally[state])
        print
    return state_distrib
    

def new_nexus_without_sites(nexus_obj, sites_to_remove):
    """
    Returns a new NexusReader instance with the sites in 
    `sites_to_remove` removed.
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 
    
    :param sites_to_remove: A list of site numbers
    :type sites_to_remove: List
    
    :return: A NexusWriter instance
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
    
    # make new nexus
    nexout = NexusWriter()
    nexout.add_comment(
        "Removed %d sites: %s" %
        (len(sites_to_remove), ",".join(["%s" % s for s in sites_to_remove]))
    )
    new_sitepos = 0
    for sitepos in range(nexus_obj.data.nchar):
        if sitepos in sites_to_remove:
            continue # skip!
        for taxon, data in nexus_obj.data:
            nexout.add(taxon, new_sitepos, data[sitepos])
        new_sitepos += 1
    return nexout



if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog old.nex [new.nex]")
    parser.add_option("-m", "--missings", dest="missings", 
            action="store_true", default=False, 
            help="Count the missing characters")
    parser.add_option("-c", "--constant", dest="constant", 
            action="store_true", default=False, 
            help="Remove the constant characters")
    parser.add_option("-u", "--unique", dest="unique", 
            action="store_true", default=False, 
            help="Remove the unique characters")
    parser.add_option("-s", "--stats", dest="stats", 
            action="store_true", default=False, 
            help="Print character-by-character stats")
    options, args = parser.parse_args()
    
    try:
        nexusname = args[0]
    except IndexError:
        print __doc__
        print "Author: %s\n" % __author__
        parser.print_help()
        sys.exit()
        
    try:
        newnexusname = args[1]
    except IndexError:
        newnexusname = None
        
    
    nexus = NexusReader(nexusname)
    newnexus = None
    
    if options.missings:
        print_missing_sites(nexus)
    elif options.constant:
        const = find_constant_sites(nexus)
        newnexus = new_nexus_without_sites(nexus, const)
        print("Constant Sites: %s" % ",".join([str(i) for i in const]))
    elif options.unique:
        unique = find_unique_sites(nexus)
        newnexus = new_nexus_without_sites(nexus, unique)
        print("Unique Sites: %s" % ",".join([str(i) for i in unique]))
    elif options.stats:
        d = print_character_stats(nexus)
        
    else:
        exit()
        
    # check for saving
    if newnexus is not None and newnexusname is not None:
        newnexus.write_to_file(newnexusname)
        print("New nexus written to %s" % newnexusname)
        
    
