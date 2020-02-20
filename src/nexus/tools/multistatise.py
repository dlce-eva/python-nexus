from nexus.writer import NexusWriter


def multistatise(nexus_obj, charlabel=None):
    """
    Returns a multistate variant of the given `nexus_obj`.

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    charlabel = charlabel or getattr(nexus_obj, 'short_filename', 1)

    states = {}
    for taxon in nexus_obj.data.matrix:
        states[taxon] = []
        sequence = nexus_obj.data.matrix[taxon]
        for site_idx, value in enumerate(sequence):
            if site_idx > 26:
                raise ValueError("Too many characters to handle! - run out of A-Z")
            assert value == str(value), "%r is not a string" % value
            if value == '1':
                states[taxon].append(chr(65 + site_idx))

    nexout = NexusWriter()
    for taxon in states:
        if not states[taxon]:
            nexout.add(taxon, charlabel, '?')
        else:
            for s in states[taxon]:
                nexout.add(taxon, charlabel, s)
    return nexout._convert_to_reader()
