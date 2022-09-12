import re
import typing
import collections

from clldutils.text import strip_brackets, split_text_with_context
import newick

from nexus.handlers import GenericHandler
from nexus.exceptions import NexusFormatException, TranslateTableException


class Tree(str):
    @classmethod
    def from_newick(cls,
                    new: typing.Union[str, newick.Node],
                    name: str = 'tree',
                    rooted: typing.Union[bool, None] = None):
        rooting = '' if rooted is None else '[&{}] '.format('R' if rooted else 'U')
        new = new if isinstance(new, str) else new.newick
        return cls('tree {} = {}{}{}'.format(name, rooting, new, '' if new.endswith(';') else ';'))

    @property
    def name(self):
        m = re.search(r'tree\s+(?P<name>[^=]+)\s*=', strip_brackets(self, {'[': ']'}))
        if m:
            return m.group('name').strip()

    @property
    def rooted(self):
        """
        Three-valued attribute, specifying whether tree is rooted, unrooted or unspecified.

        :return: `True`|`False`|`None`
        """
        m = re.search(r'\[&(?P<rooting>[RU])]', self)
        if m:
            return m.group('rooting') == 'R'
        return None

    @property
    def newick_string(self):
        # Find the string up to the first "(" which is not inside a comment ...
        prefix = split_text_with_context(self, separators='(', brackets={'[': ']'})[0]
        # ... the remainder of the line should be the newick representation of the tree:
        return self[len(prefix):].strip()

    @property
    def newick_tree(self):
        return newick.loads(self.newick_string)[0]


class TreeHandler(GenericHandler):
    """Handler for `trees` blocks"""
    is_tree = re.compile(r"""tree\s+.*=.*;""", re.IGNORECASE)

    translate_regex = re.compile(r"""
        ([,(])              # boundary
        ([A-Z0-9_\-\.]+)    # taxa-id
        :?                  # optional colon
        (\[.+?\])?          # minimally match an optional comment chunk
        (\d+(\.\d+)?)?      # optional branchlengths
        (?=[),])?           # end boundary
    """, re.IGNORECASE + re.VERBOSE + re.DOTALL)

    translate_regex_beast = re.compile(r"""
        ([,(])              # boundary
        ([A-Z0-9_\-\.]+)    # taxa-id
        (\[.+?\])           # minimally match a comment chunk
        :                   # NON-optional colon
        (\[.+?\])?          # minimally match an optional comment chunk
        (\d+(\.\d+))        # NON-optional branchlengths
        (?=[),])?           # end boundary
    """, re.IGNORECASE + re.VERBOSE + re.DOTALL)

    def __init__(self, **kw):
        super(TreeHandler, self).__init__(**kw)
        # does the treefile have a translate block?
        self.was_translated = False
        # has detranslate been called?
        self._been_detranslated = False
        self.translators = {}
        self.attributes = []
        self.trees = []

        translate_start = re.compile(r"""^translate$""", re.IGNORECASE)
        translation_pattern = re.compile(r"""(\d+)\s(['"\w\d\*\.\_\-]+)[,;]?""")

        lost_in_translation = False
        for line in self.block:
            # look for translation start, and turn on lost_in_translation
            if translate_start.match(line):
                lost_in_translation = True
                self.was_translated = True
            elif self.is_mesquite_attribute(line):
                self.attributes.append(line)

            # if we're in a translate block
            elif lost_in_translation:
                if translation_pattern.match(line):
                    taxon_id, taxon = translation_pattern.findall(line)[0]
                    taxon = taxon.strip("'")
                    if taxon_id in self.translators:
                        raise NexusFormatException(
                            "Duplicate Taxa ID %s in translate block" % taxon_id
                        )
                    if taxon in self.translators.values():
                        raise NexusFormatException(
                            "Duplicate Taxon %s in translate block" % taxon
                        )
                    self.translators[taxon_id] = taxon
                if line.endswith(';'):
                    lost_in_translation = False

            elif self.is_tree.search(line):
                self.trees.append(Tree(line))

        # if there is no translate block then get the list of taxa
        # from the first tree.
        if (not self.translators) and self.trees:
            # Rather than using a stored Tree object in self.trees, we first
            # strip the comments from the tree to make sure we have the most
            # robust parsing available.
            tree = Tree(self.remove_comments(self.trees[0]))
            for i, taxon in enumerate(tree.newick_tree.get_leaf_names(), 1):
                self.translators[i] = taxon
            self._been_detranslated = True

    def __getitem__(self, index):
        return self.trees[index]

    @property
    def taxa(self):
        return self.translators.values()

    @property
    def ntaxa(self):
        return len(self.translators.values())

    @property
    def ntrees(self):
        return len(self.trees)

    def detranslate(self):
        """Detranslates all trees in the file"""
        if not self._been_detranslated:
            for idx, tree in enumerate(self.trees):
                self.trees[idx] = Tree(self._detranslate_tree(tree, self.translators))
            self._been_detranslated = True

    @staticmethod
    def _findall_chunks(tree):
        """Helper function to find groups used by detranslate."""

        # check for beast tree or not -> decide which regex to use
        if '{' in tree and '[' in tree:  # sufficient?
            regex = TreeHandler.translate_regex_beast
            groups = ['start', 'taxon', 'comment', 'comment2', 'branch']
        else:
            regex = TreeHandler.translate_regex
            groups = ['start', 'taxon', 'comment', 'branch']

        matches = []
        index = 0
        while True:
            match = regex.search(tree, index)
            if not match:
                break
            m = dict(zip(groups, match.groups()))
            m['match'] = tree[match.start():match.end() + 1]
            m['end'] = tree[match.end()]
            matches.append(m)
            index = match.end()
        return matches

    def _detranslate_tree(self, tree, translatetable):
        """
        Takes a `tree` and expands the short format tree with translated
        taxa labels from `translatetable` into a full format tree.

        :param tree: String containing newick tree
        :type tree: String

        :param translatetable: Mapping of taxa id -> taxa names
        :type translatetable: Dict

        :return: String of detranslated tree
        """
        preamble, new = preamble_and_newick(tree)
        i = 0
        for i, found in enumerate(self._findall_chunks(new), start=1):
            if found['taxon'] in translatetable:
                taxon = translatetable[found['taxon']]
                # beast tree
                if found['comment'] and found['branch'] and 'comment2' in found:
                    sub = "{}{}:{}{}".format(
                        taxon,
                        found['comment'],
                        found['comment2'] if found['comment2'] else "",
                        found['branch'])
                elif found['comment'] and found['branch']:
                    # comment and branch
                    sub = "%s:%s%s" % \
                        (taxon, found['comment'], found['branch'])
                elif found['comment']:
                    # comment only
                    sub = "%s%s" % (taxon, found['comment'])
                elif found['branch']:
                    # branch only
                    sub = "%s:%s" % (taxon, found['branch'])
                else:
                    # taxon only
                    sub = taxon
                sub = "%s%s%s" % (found['start'], sub, found['end'])
                new = new.replace(found['match'], sub)

        if len(translatetable) and len(translatetable) != i:
            raise TranslateTableException(
                "Mismatch between translate table size (n={}) and expected taxa in trees "
                "(n={})".format(len(translatetable), i))
        return preamble + new

    def iter_lines(self):
        for attr in self.attributes:
            yield "\t" + attr
        if self.was_translated and not self._been_detranslated:
            yield '\ttranslate'
            translator_keys = [int(k) for k in self.translators.keys()]
            for i, index in enumerate(sorted(translator_keys), start=1):
                yield "\t%d %s%s" % (
                    index, self.translators[str(index)], '' if i == len(translator_keys) else ',')
            # work around bug https://github.com/CompEvol/beast2/issues/713
            yield ';'
        for tree in self.trees:
            yield "\t" + tree


def preamble_and_newick(tree):
    """
    Find (and split at) the first non-bracketed "="
    """
    brackets = {'[': ']'}
    end_brackets = {v: k for k, v in brackets.items()}
    bracket_level = collections.defaultdict(int)
    for i, c in enumerate(tree):
        if c in brackets:
            bracket_level[c] += 1
        elif c in end_brackets:
            bracket_level[end_brackets[c]] -= 1
        elif c == '=':
            if not bracket_level or (not any(bracket_level.values())):
                return tree[:i] + '=', tree[i + 1:]
    else:
        raise ValueError('invalid tree line')
