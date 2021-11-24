import random

from nexus.tools.check_zeros import check_zeros, remove_zeros
from nexus.tools.combine_nexuses import combine_nexuses
from nexus.tools.shufflenexus import shufflenexus
from nexus.tools.sites import iter_constant_sites
from nexus.tools.sites import iter_unique_sites
from nexus.tools.sites import count_site_values
from nexus.tools.sites import new_nexus_without_sites
from nexus.tools.sites import tally_by_site
from nexus.tools.sites import tally_by_taxon
from nexus.tools.sites import count_binary_set_size
from nexus.tools.util import with_nexus_reader

__all__ = [
    "binarise",
    "multistatise",
    "combine_nexuses",
    "shufflenexus",
    "iter_constant_sites",
    "iter_unique_sites",
    "count_site_values",
    "new_nexus_without_sites",
    "tally_by_site",
    "tally_by_taxon",
    "count_binary_set_size",
    "check_zeros",
    "remove_zeros",
    "delete_trees",
    "sample_trees",
    "strip_comments_in_trees",
]


@with_nexus_reader
def delete_trees(nexus_obj, delitems, log=None):
    """
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance with the given trees removed.
    """
    new = []
    if log:
        log.info('Deleting: %d trees' % len(delitems))

    for index, tree in enumerate(nexus_obj.trees, 1):
        if index in delitems:
            if log:
                log.info('Deleting tree %d' % index)
        else:
            new.append(tree)
    nexus_obj.trees.trees = new
    return nexus_obj


@with_nexus_reader
def sample_trees(nexus_obj, num_trees=None, every_nth=None, log=None):
    """
    Returns a specified number (`num_trees`) of random trees from the nexus.

    :param num_trees: The number of trees to resample
    :type num_trees: Integer

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance.

    :raises ValueError: if num_trees is larger than population
    """
    assert (num_trees or every_nth) and not (num_trees and every_nth), \
        "One of num_trees and every_nth must be selected"
    if num_trees:
        if num_trees > nexus_obj.trees.ntrees:
            raise ValueError("Treefile only has %d trees in it." % nexus_obj.trees.ntrees)
        if num_trees == nexus_obj.trees.ntrees:  # pragma: no cover
            return nexus_obj  # um. ok.
        trees = random.sample(nexus_obj.trees.trees, num_trees)
    else:
        trees = [tree for index, tree in enumerate(nexus_obj.trees, 1) if index % every_nth == 0]

    if log:
        log.info("%d trees read. Sampling %d" % (nexus_obj.trees.ntrees, len(trees)))
    nexus_obj.trees.trees = trees
    return nexus_obj


@with_nexus_reader
def strip_comments_in_trees(nexus_obj, log=None):
    """
    Removes comments from the trees in a nexus

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance with the comments removed.
    """
    new = []
    for tree in nexus_obj.trees:
        new.append(nexus_obj.trees.remove_comments(tree))

    if log:
        log.info("Removed comments")
    nexus_obj.trees.trees = new
    return nexus_obj
