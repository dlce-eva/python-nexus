import re
import warnings
import collections

from nexus.handlers import GenericHandler
from nexus.handlers import QUOTED_PATTERN, WHITESPACE_PATTERN, BEGIN_PATTERN, END_PATTERN

NTAX_PATTERN = re.compile(r"""ntax=(\d+)""", re.IGNORECASE)
NCHAR_PATTERN = re.compile(r"""nchar=(\d+)""", re.IGNORECASE)


def iter_block(lines):
    seen_matrix = False
    for line in lines:
        lline = line.lower().strip()
        if END_PATTERN.match(lline):
            continue
        elif lline.startswith('format'):
            continue
        elif BEGIN_PATTERN.match(line):
            continue
        elif lline.startswith('matrix'):
            seen_matrix = True
            continue
        yield line, lline, seen_matrix


class DataHandler(GenericHandler):
    """Handler for data matrices"""

    _character_block_pattern = re.compile(
        r"""charstatelabels(.*?);""",
        re.IGNORECASE | re.DOTALL
    )
    _format_line_pattern = re.compile(
        r"""format\b(.*?);""",
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    )

    def __init__(self, **kw):
        super(DataHandler, self).__init__(**kw)
        self.charlabels = {}
        self.attributes = []
        self.format = {}
        self.gaps = None
        self.missing = None
        self.matrix = collections.defaultdict(list)
        self._sitecache = {}  # cache for site patterns to parsed sites
        self._characters = None  # cache for characters list
        self._symbols = None  # cache for symbols list

        self.format = self.parse_format_line("\n".join(self.block))
        self.block = self._parse_charstate_block(self.block)

        _dim_taxa, _dim_chars = None, None

        read_data = False
        for line, lline, in_matrix in iter_block(self.block):
            # Dimensions line
            if lline.startswith('dimensions '):
                try:  # try for ntaxa
                    _dim_taxa = int(NTAX_PATTERN.findall(line)[0])
                except IndexError:  # pragma: no cover
                    pass
                try:  # and nchar
                    _dim_chars = int(NCHAR_PATTERN.findall(line)[0])
                except IndexError:  # pragma: no cover
                    pass
            elif self.is_mesquite_attribute(line):
                self.attributes.append(line)
            elif in_matrix:
                line = self.remove_comments(line)
                try:  # NORMALISE WHITESPACE
                    taxon, sites = WHITESPACE_PATTERN.split(line, 1)
                    read_data = True
                except ValueError:
                    continue

                taxon = QUOTED_PATTERN.sub('\\1', taxon.strip())
                self.add_taxon(taxon, self._parse_sites(sites.strip()))

        if not read_data:
            # Let's try to read a "wrapped" matrix:
            taxon, sites = None, []
            for line, lline, in_matrix in iter_block(self.block):
                if (not in_matrix) or (not lline):
                    continue  # pragma: no cover
                if not taxon:
                    assert not WHITESPACE_PATTERN.search(line.strip())
                    taxon = QUOTED_PATTERN.sub('\\1', line.strip())
                else:
                    sites.extend(self._parse_sites(line.strip()))
                    if len(sites) == _dim_chars:
                        self.add_taxon(taxon, sites)
                        taxon, sites = None, []

        # Warn if format string (ntaxa or nchar) does not give the right answer
        if _dim_taxa is not None and self.ntaxa != _dim_taxa:
            warnings.warn("Expected %d taxa, got %d" % (self.ntaxa, _dim_taxa))

        if _dim_chars is not None and self.nchar != _dim_chars:
            warnings.warn("Expected %d characters, got %d" % (self.nchar, _dim_chars))

    def __getitem__(self, index):
        return self.taxa[index], self.matrix.get(self.taxa[index])

    @property
    def ntaxa(self):
        """Number of Taxa"""
        return len(self.matrix)

    @property
    def nchar(self):
        """Number of Characters"""
        return len(self.matrix[self.taxa[0]])

    @property
    def taxa(self):
        """Taxa list"""
        return list(self.matrix.keys())

    @property
    def symbols(self):
        """Distinct symbols in matrix"""
        if not self._symbols:
            self._symbols = set()
            [self._symbols.update(vals) for vals in self.matrix.values()]
        return self._symbols

    @property
    def characters(self):
        if not self._characters:
            self._characters = collections.defaultdict(dict)
            for taxon in self.taxa:
                for index, _ in enumerate(self.matrix[taxon]):
                    label = self.charlabels.get(index, index)
                    self._characters[label][taxon] = self.matrix[taxon][index]
        return self._characters

    def is_missing_or_gap(self, state):
        return state in ('-', '?')

    def parse_format_line(self, data):
        """
        Parses a format line, and returns a dictionary of tokens

        :param data: string
        :type data: string

        :return: Returns a dictionary of tokens in the format line.
        """
        out = {}

        try:
            line = self._format_line_pattern.findall(data)[0]
        except IndexError:
            return None

        line = line.replace(" =", "=").replace("= ", "=")  # standardise
        for chunk in WHITESPACE_PATTERN.split(line):
            try:
                key, value = chunk.split("=", maxsplit=1)
                value = QUOTED_PATTERN.sub('\\1', value)
            except ValueError:
                key, value = chunk, True
            if key:
                out[key.lower()] = value
        return out

    def _parse_sites(self, sites):
        """
        Parses a string of sites and returns a list of site values

        >>> DataHandler()._parse_sites('123')
        ['1', '2', '3']
        >>> DataHandler()._parse_sites('1(12)')
        ['1', '12']
        >>> DataHandler()._parse_sites('123(4,5)56')
        ['1', '2', '3', '4,5', '5', '6']
        >>> DataHandler()._parse_sites('123(4 5)56')
        ['1', '2', '3', '4 5', '5', '6']
        >>> DataHandler()._parse_sites("ACGTU?")
        ['A', 'C', 'G', 'T', 'U', '?']

        :param sites: string
        :type sites: string

        :return: Returns a list of site values
        :raises NexusFormatException: If data matrix contains incomplete
            multistate values
        """
        remove_values = [' ', ';']
        parsed = [s for s in sites if s not in remove_values]
        if sites not in self._sitecache:
            # Slow parser for multistate
            if '(' in parsed:
                todo, parsed = parsed, []  # switch places.
                while todo:
                    site = todo.pop(0)
                    if site == ',':
                        continue
                    elif site == '(':
                        # read-ahead
                        site = ''  # discard open bracket
                        multistate = True
                        while multistate:
                            nextchar = todo.pop(0)
                            if nextchar == ')':
                                multistate = False
                            else:
                                site += nextchar
                    parsed.append(site)
                # end slow parser
        self._sitecache[sites] = parsed
        return self._sitecache[sites]

    def add_taxon(self, taxon, site_values=None):
        """
        Adds a `taxon` to the matrix with values from `site_values`

        :param taxon: taxa name
        :type data: string

        :param site_values: site values
        :type data: list

        :return: None
        """
        self.matrix[taxon].extend(site_values)

    def del_taxon(self, taxon):
        """
        Removes `taxon` from the data

        :param taxon: taxa name
        :type data: string

        :return: None
        """
        del(self.matrix[taxon])

    def _parse_charstate_block(self, data):
        """
        Extracts the character state block and returns the remaining matrix
        """
        char_number_pattern = re.compile(r"""(\d+)\s+(.*)""")
        char_index = 0

        new_data = "\n".join(data)
        charblock = self._character_block_pattern.findall(new_data)
        new_data = self._character_block_pattern.sub('', new_data)
        if len(charblock) == 1:
            charblock = charblock[0]
            for char in charblock.split(","):
                char = char.strip()
                char = char_number_pattern.sub('\\2', char)
                self.charlabels[char_index] = char
                char_index += 1
        return new_data.split("\n")

    def iter_lines(self):
        """
        Generates a string containing a nexus data block.

        :return: String
        """
        def _make_format_line(self):
            """
            Generates a format string.

            :return: String
            """
            fstring = ['\tformat']
            for key in sorted(self.format):
                value = self.format[key]
                if key == 'datatype':
                    # Datatype must come first!
                    fstring.insert(1, "%s=%s" % (key, value))
                elif key in ('interleave', ):
                    # IGNORE the interleaving -- not implemented
                    continue
                else:
                    if key == 'symbols':
                        value = '"%s"' % "".join(sorted([
                            s for s in self.symbols if not self.is_missing_or_gap(s)
                        ]))
                    fstring.append("%s=%s" % (key, value))
            return " ".join(fstring) + ";"

        for att in self.attributes:
            yield "\t%s" % att
        yield '\tdimensions ntax=%d nchar=%d;' % (self.ntaxa, self.nchar)
        yield _make_format_line(self)
        # handle char block
        if self.charlabels:
            yield '\tcharstatelabels'
            max_id = max(self.charlabels)
            for char_id in sorted(self.charlabels):
                yield '\t\t%d %s%s' % (  # zero-indexing
                    char_id + 1, self.charlabels[char_id], ',' if char_id < max_id else '')
            yield '\t;'
        yield "matrix"
        max_taxon_len = max([len(_) for _ in self.matrix])
        for taxon in sorted(self.matrix):
            yield "%s %s" % (taxon.ljust(max_taxon_len), ''.join(self.matrix[taxon]))
        yield " ;"


class CharacterHandler(DataHandler):
    pass
