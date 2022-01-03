import random
import functools

from ..handlers.tree import Tree
from .util import with_nexus_reader


def replace_trees(func):
    """
    Decorator for generators yielding a mutated set of trees for a nexus object.

    :param func: A generator function that yields the new `Tree` objects.
    """
    @functools.wraps(func)
    def _(nexus_obj, *args, **kwargs):
        new = []
        for tree in func(nexus_obj, *args, **kwargs):
            assert isinstance(tree, Tree), 'tree manipulators must yield nexus.handlers.tree.Tree s'
            new.append(tree)
        nexus_obj.trees.trees = new
        return nexus_obj
    return _


@with_nexus_reader
@replace_trees
def visit_trees(nexus_obj, visitor, log=None):
    """
    Manipulate all trees in a `NexusReader` by running a callable with the following signature:

    .. code-block:: python

        def visitor(tree: newick.Node) -> typing.Union[newick.Node, str, None]: pass

    If the visitor returns `None`, the tree is deleted, otherwise replaced with the returned
    newick representation.
    """
    for tree in nexus_obj.trees:
        res = visitor(tree.newick_tree)
        if res:
            yield Tree.from_newick(res, name=tree.name, rooted=tree.rooted)


@with_nexus_reader
@replace_trees
def visit_tree_nodes(nexus_obj, visitor, log=None):
    """
    Manipulate all trees in a `NexusReader` by running a callable on each node of each tree.

    :param visitor: callable suitable for passing into `newick.Node.visit`.
    """
    for tree in nexus_obj.trees:
        ntree = tree.newick_tree
        ntree.visit(visitor)
        yield Tree.from_newick(ntree, name=tree.name, rooted=tree.rooted)


@with_nexus_reader
@replace_trees
def delete_trees(nexus_obj, delitems, log=None):
    """
    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance with the given trees removed.
    """
    if log:
        log.info('Deleting: %d trees' % len(delitems))

    for index, tree in enumerate(nexus_obj.trees, 1):
        if index in delitems:
            if log:
                log.info('Deleting tree %d' % index)
        else:
            yield tree



def _sample_trees(trees, num_trees=None, every_nth=None):
    """
    Returns a specified number (`num_trees`) of random trees from the nexus,
    or samples `every_nth` tree from the nexus file.
    
    Intended for internal use only, the wrapper `sample_trees` is intended for 
    general use.

    :param trees: A list of trees
    :type trees: List

    :param num_trees: The number of trees to resample
    :type num_trees: Integer

    :param every_nth: The number of trees to at every step.
    :type every_nth: Integer

    :return: A generator of trees

    :raises ValueError: if num_trees is larger than population
    :raises ValueError: if both num_trees and every_nth is specified.
    :raises ValueError: if neither num_trees nor every_nth is specified.
    """
    ntrees = len(trees)
    if num_trees and every_nth:
        raise ValueError("Can only handle one operation (`num_trees` OR `every_nth`) at once.")
    elif num_trees:
        if num_trees > ntrees:
            raise ValueError("Treefile only has %d trees in it." % ntrees)
        yield from random.sample(trees, num_trees)
    elif every_nth:
        yield from [tree for index, tree in enumerate(trees, 1) if index % every_nth == 0]
    else:
        raise ValueError("One of num_trees and every_nth must be selected.")
    

# wraps _sample trees to handle CLI niceties like @with_nexus_reader
@with_nexus_reader
@replace_trees
def sample_trees(nexus_obj, num_trees=None, every_nth=None, log=None):
    """
    Returns a specified number (`num_trees`) of random trees from the nexus,
    or samples `every_nth` tree from the nexus file.

    :param nexus_obj: A `NexusReader` instance.
    :type nexus_obj: NexusReader

    :param num_trees: The number of trees to resample
    :type num_trees: Integer

    :param every_nth: The number of trees to at every step.
    :type every_nth: Integer

    :return: A generator of trees
    """
    if log:
        if num_trees:
            log.info("%d trees read. Sampling %d" % (nexus_obj.trees.ntrees, num_trees))
        elif every_nth:
            log.info("%d trees read. Sampling every %d" % (nexus_obj.trees.ntrees, every_nth))

    yield from _sample_trees(nexus_obj.trees.trees, num_trees=num_trees, every_nth=every_nth)


@with_nexus_reader
@replace_trees
def strip_comments_in_trees(nexus_obj, log=None):
    """
    Removes comments from the trees in a nexus

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance with the comments removed.
    """
    for tree in nexus_obj.trees:
        yield Tree(nexus_obj.trees.remove_comments(tree))

    if log:
        log.info("Removed comments")
