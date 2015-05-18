from nexus import NexusWriter
from nexus.tools import check_for_valid_NexusReader

# set isstr in a python 2 vs python 3 safe way
try:
    basestring  # attempt to evaluate basestring
    def isstr(s):  # py2
        return isinstance(s, basestring)
except NameError:
    def isstr(s):  # py3
        return isinstance(s, str)


def _recode_to_binary(char, keep_zero=False):
    """
    Recodes a dictionary to binary data.

    :param char: A dictionary of taxa to state values
    :type char: dict

    :param keep_zero: A boolean flag denoting whether to
        treat '0' as a missing state or not. The default
        (False) is to ignore '0' as a trait absence.

        Setting this to True will treat '0' as a unique
        state.
    :type keep_zero: Boolean

    :return: A dictionary of taxa to recoded values.
    :raises ValueError: if any of the states in the
        `char` dictionary is not a string (i.e.
        integer or None values)

    >>> recode = _recode_to_binary({'Maori': '1', 'Dutch': '2', 'Latin': '1'})
    >>> recode['Maori']
    '10'
    >>> recode['Dutch']
    '01'
    >>> recode['Latin']
    '10'
    """

    newdata = {}

    # unwanted states
    unwanted_states = ['-', '?']
    if not keep_zero:
        unwanted_states.append('0')
    
    if not all(isstr(v) for v in char.values()):
        raise ValueError('Data must be strings')

    # preproccess taxa states and get unique states
    states = set()
    for taxon, value in char.items():
        char[taxon] = [v for v in value.replace(" ", ",").split(",")
                            if v not in unwanted_states]
        states.update(char[taxon])

    states = sorted(states)
    num_states = len(states)
    for taxon, values in char.items():
        newdata[taxon] = ['0' for x in range(num_states)]
        for value in values:
            if value not in unwanted_states:  # ignore missing values
                newdata[taxon][states.index(value)] = '1'
        newdata[taxon] = "".join(newdata[taxon])
        assert len(newdata[taxon]) == num_states

    return newdata

def binarise(nexus_obj, one_nexus_per_block=False, keep_zero=False):
    """
    Returns a binary variant of the given `nexus_obj`.
    If `one_nexus_per_block` then we return a list of NexusWriter instances.

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :param one_nexus_per_block: Whether to return a single NexusWriter, or a
                                list of NexusWriter's (one per character)
    :type one_nexus_per_block: Boolean

    :param keep_zero: A boolean flag denoting whether to
        treat '0' as a missing state or not. The default
        (False) is to ignore '0' as a trait absence.

        Setting this to True will treat '0' as a unique
        state.
    :type keep_zero: Boolean

    :return: A NexusWriter instance or a list of NexusWriter instances.
    :raises AssertionError: if nexus_obj is not a nexus
    :raises NexusFormatException: if nexus_obj does not have a `data` block
    """
    check_for_valid_NexusReader(nexus_obj, required_blocks=['data'])
    nexuslist = []
    n = NexusWriter()

    for i in sorted(nexus_obj.data.charlabels):
        label = nexus_obj.data.charlabels[i]  # character label
        char = nexus_obj.data.characters[label]  # character dict
        recoding = _recode_to_binary(char, keep_zero)  # recode
        
        new_char_length = len(recoding[list(recoding.keys())[0]])
        
        # loop over recoded data
        for j in range(new_char_length):
            for taxon, state in recoding.items():
                # make new label
                new_label = "%s_%d" % (str(label), j)
                # add to nexus
                n.add(taxon, new_label, state[j])

        if one_nexus_per_block:
            nexuslist.append(n)
            n = NexusWriter()

    if one_nexus_per_block:
        return nexuslist
    else:
        return n

