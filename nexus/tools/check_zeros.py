from collections import Counter

from nexus.tools import check_for_valid_NexusReader

def check_zeros(nexus_obj, absences=None, missing=None):
    """
    Checks for sites in the nexus that are coded as all empty.
    
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader
    
    :param absences: A list of values to be marked as absent.
        Default = ["0"]
    :type char: list
    
    :param missing: A list of values to be marked as missing.
        Default = ["-", "?"]
    :type char: list
    
    :return: A list of site indexes
    :raises ValueError: if any of the states in the
        `char` dictionary is not a string (i.e.
        integer or None values)
    """
    check_for_valid_NexusReader(nexus_obj, required_blocks=['data'])
    
    if absences is None:
        absences = ['0']
    if missing is None:
        missing = ['-', '?']
    
    bad = []
    for site_idx, site in enumerate(nexus_obj.data.characters, 0):
        states = Counter(nexus_obj.data.characters[site].values())
        zeros = sum([
            states[k] for k in states if k in absences or k in missing
        ])
        total = sum(states.values())
        if zeros == total:
            bad.append(site_idx)
    return bad


