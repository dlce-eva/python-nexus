"""
Tools for writing a nexus file
"""
import collections

from nexus.util import FileWriterMixin

TEMPLATE = """
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
%(matrix)s
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
        self._taxa = None
        self.data = collections.defaultdict(dict)
        self.is_binary = False
        self.trees = []

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
        return list(self.data.keys())

    @property
    def ntrees(self):
        return len(self.trees)

    @property
    def taxa(self):
        if self._taxa is None:
            self._taxa = set()
            [self._taxa.update(self.data[c].keys()) for c in self.data]
        return self._taxa

    @property
    def symbols(self):
        symbols = set()
        [symbols.update(self.data[c].values()) for c in self.data]
        symbols = [s for s in symbols if s not in ('-', '?')]
        return symbols

    def _iter_charlabels(self):
        """Generates a character label block"""
        yield "CHARSTATELABELS"
        for i, char in enumerate(sorted(self.characters), 1):
            yield "\t\t%d %s%s" % (
                i, self.clean(str(char)), '' if i == len(self.characters) else ',')
        yield ";"

    def _iter_matrix(self, interleave):
        """Generates a matrix block"""
        max_taxon_size = max([len(t) for t in self.taxa]) + 3

        if interleave:
            for c in sorted(self.characters):
                for t in self.taxa:
                    yield "%s %s" % (t.ljust(max_taxon_size), self.data[c].get(t, self.MISSING))
                yield ""
        else:
            for t in sorted(self.taxa):
                s = []
                for c in sorted(self.characters):
                    value = self.data[c].get(t, self.MISSING)
                    if len(value) > 1:  # wrap equivocal states in ()'s
                        value = "(%s)" % value
                    s.append(value)
                yield "%s %s" % (t.ljust(max_taxon_size), ''.join(s))

    def make_treeblock(self):
        return "\n".join(["    %s" % t.lstrip().strip() for t in self.trees])

    def _make_comments(self):
        """Generates a comments block"""
        return "\n".join(["[%s]" % c.ljust(70) for c in self.comments])

    def add_comment(self, comment):
        """Adds a `comment` into the nexus file"""
        self.comments.append(comment)

    def add(self, taxon, character, value):
        """Adds a `character` for the given `taxon` and sets it to `value`"""
        assert self.is_binary is False, "Unable to add data to a binarised nexus form"
        value = str(value)
        # have multiple entries
        if taxon in self.data[character]:
            self.data[character][taxon] += value
        else:
            self.data[character][taxon] = value

    def remove(self, taxon, character):
        """Removes a `character` for the given `taxon` and sets it to empty"""
        del(self.data[character][taxon])

    def remove_taxon(self, taxon):
        """Removes a given `taxon` from the nexus file"""
        for char in self.data:
            del(self.data[char][taxon])

    def remove_character(self, character):
        """Removes a given `character` from the nexus file"""
        del(self.data[character])

    def write(self, interleave=False, charblock=False, **kw):
        """
        Generates a string representation of the nexus
        (basically a wrapper around make_nexus)

        :param interleave: Generate interleaved matrix or not
        :param charblock: Include a characters block or not

        :return: String
        """
        return self.make_nexus(interleave, charblock)

    def _is_valid(self):
        """Checks the nexus is valid to write (i.e. not empty)"""
        if self.data and self.taxa:
            return True
        if self.ntrees:
            return True
        return False

    def make_nexus(self, interleave=False, charblock=False):
        """
        Generates a string representation of the nexus

        :param interleave: Generate interleaved matrix or not
        :type interleave: Boolean
        :param charblock: Include a characters block or not
        :type charblock: Boolean

        :return: String
        """
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
                'missing': self.MISSING,
                'gap': self.GAP,
                'datatype': self.DATATYPE,
            }
        else:
            datablock = ""

        treeblock = TREE_TEMPLATE % {'trees': self.make_treeblock()} if self.ntrees else ""
        return TEMPLATE % {'datablock': datablock, 'treeblock': treeblock}

    def write_as_table(self):
        """
        Generates a simple table of the nexus
        """
        out = []
        for t in sorted(self.taxa):
            s = []
            for c in sorted(self.characters):
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
        return NexusReader.from_string(self.make_nexus(interleave=False, charblock=True))
