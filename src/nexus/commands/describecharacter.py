"""
Describes the given character.
"""
import textwrap
import collections

from nexus.cli_util import add_nexus, get_reader

wrapper = textwrap.TextWrapper(initial_indent="  ", subsequent_indent="  ")


def register(parser):
    parser.add_argument('site_index', help="Character index")
    add_nexus(parser)


def run(args):
    print_character_stats(get_reader(args, required_blocks=['data']), args.site_index)


def print_character_stats(nexus_obj, character_index):
    """
    Prints the character/site statistics for a given `nexus_obj` and
    character index

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :param character_index: The character index of the character to summarise
    :type character_index: Int or String

    :raises IndexError: if character_index is not in nexus data block
    """
    index = None
    if character_index in nexus_obj.data.characters:
        index = character_index  # string index
    else:
        try:
            character_index = int(character_index)
        except ValueError:  # pragma: no cover
            pass

        if character_index in nexus_obj.data.characters:
            index = character_index

    if index is None:
        raise IndexError("Character '%s' is not in the nexus" % character_index)

    states = collections.defaultdict(list)
    for taxon, state in nexus_obj.data.characters[index].items():
        states[state].append(taxon)

    for state in sorted(states):
        print('State: %s (%d / %d = %0.2f)' % (
            state,
            len(states[state]), nexus_obj.data.ntaxa,
            (len(states[state]) / nexus_obj.data.ntaxa * 100)
        ))
        print("\n".join(wrapper.wrap(", ".join(sorted(states[state])))))
        print("\n")
    return
