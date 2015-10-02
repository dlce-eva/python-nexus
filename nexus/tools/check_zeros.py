from collections import Counter

from nexus.tools import check_for_valid_NexusReader
from nexus.tools import new_nexus_without_sites

def check_zeros(nexus_obj, absences=None, missing=None):
    """
    Checks for sites in the nexus that are coded as all empty.

    Returns a list of sites that are completely empty. Note that
    this is zero-indexed (i.e. the first site is site 0 not 1)
    to enable indexing of nexus.data.matrix/.character lists
    
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

def remove_zeros(nexus_obj, absences=None, missing=None):
    """
    Removes sites in the nexus that are coded as all empty.
   
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader
    
    :param absences: A list of values to be marked as absent.
        Defacult = ["0"]
    :type char: list
    
    :param missing: A list of values to be marked as missing.
        Default = ["-", "?"]
    :type char: list
    
    :return: a new nexus
    """
    zeros = check_zeros(nexus_obj, absences=absences, missing=missing)
    return new_nexus_without_sites(nexus_obj, zeros)._convert_to_reader()

