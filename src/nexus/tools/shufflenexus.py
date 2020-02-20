import random

from nexus.writer import NexusWriter


def shufflenexus(nexus_obj, resample=False):
    """
    Shuffles the characters between each taxon to create a new nexus

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :param resample: The number of characters to resample. If set to False,
        then the number of characters will equal the number of characters
        in the original data file.
    :type resample: Integer

    :return: A shuffled NexusReader instance
    :raises ValueError: if resample is not False or a positive Integer
    """
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
        character = random.randrange(0, nexus_obj.data.nchar)
        chars = nexus_obj.data.characters[character]
        site_values = [chars[taxon] for taxon in nexus_obj.data.taxa]
        random.shuffle(site_values)
        for taxon in nexus_obj.data.taxa:
            newnexus.add(taxon, i, site_values.pop(0))
    return newnexus
