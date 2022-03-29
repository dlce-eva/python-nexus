"""
Tools for writing a nexus file
"""
import collections

from nexus.util import FileWriterMixin

TEMPLATE = """\
#NEXUS
%(datablock)s
%(treeblock)s
"""

DATA_TEMPLATE = """
%(comments)s

BEGIN DATA;
  DIMENSIONS NTAX=%(ntax)d NCHAR=%(nchar)d;
  FORMAT DATATYPE=%(datatype)s MISSING=%(missing)s GAP=%(gap)s %(interleave)s SYMBOLS="%(symbols)s";
  %(charblock)s
MATRIX
%(collabels)s%(matrix)s%(collabels)s
;
END;
"""

TREE_TEMPLATE = """
BEGIN TREES;
%(trees)s
END;
"""


class NexusWriter(FileWriterMixin):

    MISSING = '?'
    GAP = '-'
    DATATYPE = 'STANDARD'

    def __init__(self):
        self.comments = []
        self.collabels = []
        self._taxa = None
        self._characters = None
        self.data = collections.defaultdict(dict)
        self.is_binary = False
        self.trees = []
        self._taxa_in = []
        self._chars_in = []
        self.preserve_order = False
        self.padding = 3

    def clean(self, s):
        """Removes unsafe characters"""
        _EMPTY = ''
        replacements = {
            ' ': _EMPTY, '\\': _EMPTY, ':': _EMPTY,
            '/': _EMPTY, '?': _EMPTY, '-': _EMPTY,
            '(': '_', ')': _EMPTY,
        }
        for f, t in replacements.items():
            s = s.replace(f, t)
        return s

    @property
    def characters(self):
        if self._characters is None:
            self._characters = list(sorted(self.data.keys(), key=lambda x: self._chars_in.index(x)
                                           if self.preserve_order else x))
        return self._characters

    @property
    def ntrees(self):
        return len(self.trees)

    @property
    def taxa(self):
        if self._taxa is None:
            self._taxa = set()
            [self._taxa.update(self.data[c].keys()) for c in self.data]
            self._taxa = list(sorted(self._taxa, key=lambda x: self._taxa_in.index(x)
                                     if self.preserve_order else x))
        return self._taxa

    @property
    def symbols(self):
        symbols = set()
        [symbols.update(self.data[c].values()) for c in self.data]
        symbols = [s for s in symbols if s not in ('-', '?')]
        return symbols

    def _iter_charlabels(self):
        """Generates a character label block"""
        chars_len = len(self.characters)
        yield "CHARSTATELABELS"
        for i, char in enumerate(self.characters, 1):
            yield "    %d %s%s" % (
                i, self.clean(str(char)), '' if i == chars_len else ',')
        yield ";"

    def _iter_matrix(self, interleave):
        """Generates a matrix block"""
        max_taxon_size = max([len(t) for t in self.taxa]) + self.padding

        if interleave:
            for c in self.characters:
                for t in self.taxa:
                    yield "%s %s" % (t.ljust(max_taxon_size), self.data[c].get(t, self.MISSING))
                yield ""
        else:
            for t in self.taxa:
                s = []
                for c in self.characters:
                    value = self.data[c].get(t, self.MISSING)
                    if len(value) > 1:  # wrap equivocal states in ()'s
                        value = "(%s)" % value
                    s.append(value)
                yield "%s %s" % (t.ljust(max_taxon_size), ''.join(s))

    def make_treeblock(self):
        return "\n".join(["    %s" % t.lstrip().strip() for t in self.trees])

    def _make_comments(self):
        """Generates a comments block"""
        return "\n".join(["[%s]" % c.ljust(70) if len(c) else "" for c in self.comments])

    def add_comment(self, comment):
        """Adds a `comment` into the nexus file"""
        self.comments.append(comment)

    def _make_collabels(self):
        """Generates a matrix column labels block as comment"""
        pad = " " * (max([len(t) for t in self.taxa]) + self.padding)
        return "\n".join(["%s[%s]" % (pad, c) if len(c) else "" for c in self.collabels])

    def add_collabels(self, collabel):
        """
        Adds a `matrix column label` as comment into the nexus file
        (each row has to be calculated by the user in beforehand,
        padding will be done automatically)
        """
        if isinstance(collabel, list):
            self.collabels.extend(collabel)
        else:
            self.collabels.append(collabel)

    def add(self, taxon, character, value, check=False):
        """Adds a `character` for the given `taxon` and sets it to `value`"""
        assert self.is_binary is False, "Unable to add data to a binarised nexus form"
        if check:
            assert isinstance(character, (str, int)), 'Character must not be of type {}'.format(
                type(character))
            if self.characters:
                assert all(isinstance(c, str) for c in [character] + self.characters) or \
                    all(isinstance(c, int) for c in [character] + self.characters), \
                    "Characters of mixed type are not supported"
        value = str(value)

        if taxon not in self._taxa_in:
            self._taxa_in.append(taxon)
        if character not in self.data:
            self._chars_in.append(character)

        self._taxa = None
        self._characters = None

        # have multiple entries
        if taxon in self.data[character]:
            self.data[character][taxon] += value
        else:
            self.data[character][taxon] = value

    def remove(self, taxon, character):
        """Removes a `character` for the given `taxon` and sets it to empty"""
        del(self.data[character][taxon])
        self._taxa = None
        self._characters = None
        for char in self.data:
            if taxon in self.data[char]:
                break
        else:
            self._taxa_in.remove(taxon)

    def remove_taxon(self, taxon):
        """Removes a given `taxon` from the nexus file"""
        for char in self.data:
            del(self.data[char][taxon])
        self._taxa = None
        self._taxa_in.remove(taxon)

    def remove_character(self, character):
        """Removes a given `character` from the nexus file"""
        del(self.data[character])
        self._characters = None
        self._chars_in.remove(character)

    def write(self, interleave=False, charblock=False, preserve_order=False, **kw):
        """
        Generates a string representation of the nexus
        (basically a wrapper around make_nexus)

        :param interleave: Generate interleaved matrix or not
        :type interleave: Boolean
        :param charblock: Include a characters block or not
        :type charblock: Boolean
        :param preserve_order: Preserve input order of taxa and characters or not
        :type preserve_order: Boolean

        :return: String
        """
        return self.make_nexus(interleave, charblock, preserve_order)

    def _is_valid(self):
        """Checks the nexus is valid to write (i.e. not empty)"""
        if self.data and self.taxa:
            return True
        if self.ntrees:
            return True
        return False

    def make_nexus(self, interleave=False, charblock=False, preserve_order=False):
        """
        Generates a string representation of the nexus

        :param interleave: Generate interleaved matrix or not
        :type interleave: Boolean
        :param charblock: Include a characters block or not
        :type charblock: Boolean
        :param preserve_order: Preserve input order of taxa and characters or not
        :type preserve_order: Boolean

        :return: String
        """
        self.preserve_order = preserve_order

        if not self._is_valid():
            raise ValueError("Nexus has no data!")

        if self.data:
            datablock = DATA_TEMPLATE % {
                'ntax': len(self.taxa),
                'nchar': len(self.characters),
                'charblock': '\n'.join(self._iter_charlabels()) if charblock else '',
                'matrix': '\n'.join(self._iter_matrix(interleave=interleave)),
                'interleave': 'INTERLEAVE' if interleave else '',
                'comments': self._make_comments(),
                'symbols': ''.join(sorted(self.symbols)),
                'collabels': self._make_collabels() if self.collabels else '',
                'missing': self.MISSING,
                'gap': self.GAP,
                'datatype': self.DATATYPE,
            }
        else:
            datablock = ""

        treeblock = TREE_TEMPLATE % {'trees': self.make_treeblock()} if self.ntrees else ""
        return TEMPLATE % {'datablock': datablock, 'treeblock': treeblock}

    def write_as_table(self, preserve_order=False):
        """
        Generates a simple table of the nexus

        :param preserve_order: Preserve input order of taxa and characters or not
        :type preserve_order: Boolean
        """
        self.preserve_order = preserve_order
        out = []
        for t in self.taxa:
            s = []
            for c in self.characters:
                value = self.data[c].get(t, self.MISSING)
                if len(value) > 1:  # wrap equivocal states in ()'s
                    value = "(%s)" % value
                s.append(value)
            out.append("%s %s" % (t.ljust(25), ''.join(s)))
        return "\n".join(out)

    def _convert_to_reader(self):
        """
        This is a hack to convert a NexusWriter object to a NexusReader
        instance.

        One day I'll refactor this all so Reader and Writer subclass something,
        which will make this unnecessary.
        """
        from .reader import NexusReader
        return NexusReader.from_string(
            self.make_nexus(interleave=False, charblock=True, preserve_order=False))
