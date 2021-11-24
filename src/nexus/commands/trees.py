"""
Performs some functions on trees
"""
from clldutils.clilib import add_random_seed
from nexus.cli_util import add_nexus, get_reader, add_output, write_output, list_of_ranges
from nexus.tools import delete_trees, sample_trees, strip_comments_in_trees


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
    add_random_seed(parser)
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
        nexus = delete_trees(nexus, args.deltree, log=args.log)

    if args.resample:
        nexus = sample_trees(nexus, every_nth=args.resample, log=args.log)

    if args.random:
        nexus = sample_trees(nexus, num_trees=args.random, log=args.log)

    if args.removecomments:
        nexus = strip_comments_in_trees(nexus, log=args.log)

    if args.detranslate:
        nexus.trees.detranslate()

    write_output(nexus, args)
