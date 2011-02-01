import os

from random import shuffle, randrange

from reader import NexusReader, NexusFormatException
from writer import NexusWriter

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
    charpos = 0
    for nex_id, nex in enumerate(nexuslist, 1):
        if isinstance(nex, NexusReader) == False:
            raise TypeError("%s is not a NexusReader instance" % nex)
        
        if 'data' not in nex.blocks:
            raise NexusFormatException("Error: %s has no data block" % nex.filename)
        
        out.add_comment("%d - %d: %s" % (charpos, charpos + nex.data.nchar -1, nex.filename))
        
        if hasattr(nex, 'short_filename'):
            nexus_label = os.path.splitext(nex.short_filename)[0]
        else:
            nexus_label = str(nex_id)
            
        for site_idx, site in enumerate(sorted(nex.data.characters), 0):
            data = nex.data.characters.get(site)
            charpos += 1
            # work out character label
            charlabel = nex.data.charlabels.get(site_idx, site_idx + 1)
            label = '%s.%s' % (nexus_label, charlabel)
            
            for taxon, value in data.items():
                out.add(taxon, label, value)
    return out


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


def multistatise(nexus_obj):
    """
    Returns a multistate variant of the given `nexus_obj`.

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader 

    :return: A NexusReader instance
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """

    assert isinstance(nexus_obj, NexusReader), "Nexus_obj should be a NexusReader instance"
    if hasattr(nexus_obj, 'data') == False:
        raise NexusFormatException("Nexus has no `data` block")
        
    site_idx = 0
    nexout = NexusWriter()
    missing = []
    
    charlabel = getattr(nexus_obj, 'short_filename', 1)
    
    for site, data in nexus_obj.data.characters.items():
        multistate_value = chr(65 + site_idx)
        for taxon, value in data.items():
            assert value == str(value)
            if value in ('?', '-'):
                missing.append(taxon)
                
            if value == '1':
                nexout.add(taxon, charlabel, multistate_value)
                if taxon in missing: # remove taxon if we've seen a non-? entry
                    missing.remove(taxon)
        site_idx += 1
        assert site_idx < 26, "Too many characters to handle! - run out of A-Z"
        
    # add missing state for anything that is all missing, and has not been
    # observed anywhere
    for taxon in nexus_obj.data.taxa:
        if taxon not in nexout.data[str(charlabel)]:
            nexout.add(taxon, charlabel, '?')
    return nexout._convert_to_reader()
    
    
    
    
