from nexus import NexusWriter
from nexus.tools import check_for_valid_NexusReader

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
    check_for_valid_NexusReader(nexus_obj, required_blocks=['data'])

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

