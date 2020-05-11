"""
Performs some functions on trees
"""
from random import sample

from nexus.cli_util import add_nexus, get_reader, add_output, write_output, list_of_ranges


def register(parser):
    add_output(parser)
    add_nexus(parser)
    parser.add_argument(
        "-d", "--deltree",
        default=[],
        type=list_of_ranges,
        help="Remove the trees specified as comma-separated ranges of 1-based indices, "
             "e.g. '1', '1-5', '1,20-30'")
    parser.add_argument(
        "-r", "--resample",
        type=int,
        default=0,
        help="Resample the trees every Nth tree")
    parser.add_argument(
        "-n", "--random",
        type=int,
        default=0,
        help="Randomly sample N trees from the treefile")
    parser.add_argument(
        "-c", "--removecomments",
        action="store_true",
        default=False,
        help="Remove comments from the trees")
    parser.add_argument(
        "-t", "--detranslate",
        action="store_true",
        default=False,
        help="Remove taxa translation block from the trees")


def run(args):
    nexus = get_reader(args, required_blocks=['trees'])
    args.log.info("{0} trees found with {1} translated taxa".format(
        nexus.trees.ntrees, len(nexus.trees.translators)))

    if args.deltree:
        nexus = run_deltree(args.deltree, nexus, args.log)

    if args.resample:
        nexus = run_resample(args.resample, nexus, args.log)

    if args.random:
        nexus = run_random(args.random, nexus, args.log)

    if args.removecomments:
        nexus = run_removecomments(nexus, args.log)

    if args.detranslate:
        nexus.trees.detranslate()

    write_output(nexus, args)


def run_deltree(delitems, nexus_obj, log):
    """
    Returns a list of trees to be deleted

    :param deltree: A string of trees to be deleted.
    :type deltree: String

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance with the given trees removed.
    """
    new = []
    log.info('Deleting: %d trees' % len(delitems))

    for index, tree in enumerate(nexus_obj.trees, 1):
        if index in delitems:
            log.info('Deleting tree %d' % index)
        else:
            new.append(tree)
    nexus_obj.trees.trees = new
    return nexus_obj


def run_resample(resample, nexus_obj, log):
    """
    Resamples the trees in a nexus

    :param resample: Resample every `resample` trees
    :type resample: Integer

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance with the given trees removed.
    """
    new = []
    log.info('Resampling ever %d trees' % resample)

    ignore_count = 0
    for index, tree in enumerate(nexus_obj.trees, 1):
        if index % resample == 0:
            new.append(tree)
        else:
            ignore_count += 1

    log.info("Ignored %d trees" % ignore_count)
    nexus_obj.trees.trees = new
    return nexus_obj


def run_removecomments(nexus_obj, log):
    """
    Removes comments from the trees in a nexus

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance with the comments removed.
    """
    new = []
    for tree in nexus_obj.trees:
        new.append(nexus_obj.trees.remove_comments(tree))

    log.info("Removed comments")
    nexus_obj.trees.trees = new
    return nexus_obj


def run_random(num_trees, nexus_obj, log):
    """
    Returns a specified number (`num_trees`) of random trees from the nexus.

    :param num_trees: The number of trees to resample
    :type num_trees: Integer

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A NexusReader instance.

    :raises ValueError: if num_trees is larger than population
    """
    if num_trees > nexus_obj.trees.ntrees:
        raise ValueError("Treefile only has %d trees in it." % nexus_obj.trees.ntrees)
    elif num_trees == nexus_obj.trees.ntrees:  # pragma: no cover
        return nexus_obj  # um. ok.
    else:
        log.info("%d trees read. Sampling %d" % (nexus_obj.trees.ntrees, num_trees))
        nexus_obj.trees.trees = sample(nexus_obj.trees.trees, num_trees)
    return nexus_obj
