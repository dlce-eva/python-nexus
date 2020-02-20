"""
Performs a number of nexus manipulation methods.
"""
import collections

from nexus.cli_util import add_nexus, get_reader, add_output, write_output, list_of_ranges
from nexus.tools import count_site_values
from nexus.tools import check_zeros
from nexus.tools import iter_constant_sites
from nexus.tools import iter_unique_sites
from nexus.tools import new_nexus_without_sites


def register(parser):
    add_output(parser)
    add_nexus(parser)
    parser.add_argument(
        "-n", "--number",
        action="store_true",
        default=False,
        help="Count the number of characters")
    parser.add_argument(
        "-c", "--constant",
        action="store_true",
        default=False,
        help="Remove the constant characters")
    parser.add_argument(
        "-u", "--unique",
        action="store_true",
        default=False,
        help="Remove the unique characters")
    parser.add_argument(
        "-x", "--remove",
        type=list_of_ranges,
        help="Remove characters specified as comma-separated ranges of 1-based indices, "
             "e.g. '1', '1-5', '1,20-30'")
    parser.add_argument(
        "-z", "--zeros",
        action="store_true",
        default=False,
        help="Remove the zero characters")
    parser.add_argument(
        "-s", "--stats",
        action="store_true",
        default=False,
        help="Print character-by-character stats")


def run(args):
    nexus = get_reader(args)

    if args.number:
        print_site_values(nexus)
        return 0

    if args.stats:
        print_character_stats(nexus)
        return 0

    const, unique, zeros, remove = [], [], [], []
    if args.constant:
        const = list(iter_constant_sites(nexus))
        if const:
            args.log.info("Constant Sites: %s" % ",".join([str(i + 1) for i in const]))
    if args.unique:
        unique = list(iter_unique_sites(nexus))
        if unique:
            args.log.info("Unique Sites: %s" % ",".join([str(i + 1) for i in unique]))
    if args.zeros:
        zeros = check_zeros(nexus)
        if zeros:
            args.log.info("Zero Sites: %s" % ",".join([str(i + 1) for i in zeros]))
    if args.remove:
        args.log.info("Remove: %s" % ",".join([str(i) for i in args.remove]))
        remove = [i - 1 for i in args.remove]  # translate to zero-based indices.

    write_output(new_nexus_without_sites(nexus, set(const + unique + zeros + remove)), args)


def print_site_values(nexus_obj, characters=None):
    """
    Prints out counts of the number of sites with state in `characters` in a
    nexus.

    (Wrapper around `count_site_values`)

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader
    """
    characters = characters if characters is not None else ['-', '?']

    count = count_site_values(nexus_obj, characters)
    print("Number of %s in %s" % (",".join(characters), nexus_obj.filename))
    for taxon in sorted(count):
        prop = (count[taxon] / nexus_obj.data.nchar) * 100
        print(
            "%s: %d/%d (%0.2f%%)" %
            (taxon.ljust(20), count[taxon], nexus_obj.data.nchar, prop)
        )
    print('-' * 76)
    total_count = sum([x for x in count.values()])
    total_data = nexus_obj.data.nchar * nexus_obj.data.ntaxa
    prop = (total_count / total_data) * 100
    print('TOTAL: %d/%d (%0.2f%%)' %
          (total_count, total_data, prop)
          )


def print_character_stats(nexus_obj):
    """
    Prints the number of states and members for each site in `nexus_obj`

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A list of the state distribution
    """
    state_distrib = []
    for i in range(0, nexus_obj.data.nchar):
        tally = collections.Counter()
        for taxa, characters in nexus_obj.data:
            tally.update([characters[i]])

        print("%5d" % i, end="")
        for state in tally:
            print("%sx%d" % (state, tally[state]), end="")
            state_distrib.append(tally[state])
        print("\n")
    return state_distrib
