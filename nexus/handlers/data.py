import re
import warnings
from collections import defaultdict
from nexus.handlers import GenericHandler
from nexus.handlers import QUOTED_PATTERN, WHITESPACE_PATTERN, BEGIN_PATTERN
from nexus.exceptions import NexusFormatException

NTAX_PATTERN = re.compile(r"""ntax=(\d+)""", re.IGNORECASE)
NCHAR_PATTERN = re.compile(r"""nchar=(\d+)""", re.IGNORECASE)


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
    
    def __init__(self):
        self.charlabels = {}
        self.attributes = []
        self.format = {}
        self.gaps = None
        self.missing = None
        self.matrix = defaultdict(list)
        # private
        super(DataHandler, self).__init__()

    def __getitem__(self, index):
        return (self.taxa[index], self.matrix.get(self.taxa[index]))

    @property
    def ntaxa(self):
        """Number of Taxa"""
        return len(self.matrix)

    @property
    def nchar(self):
        """Number of Characters"""
        return len(self.matrix[list(self.matrix.keys())[0]])
    
    @property
    def taxa(self):
        """Taxa list"""
        return list(self.matrix.keys())
    
    @property
    def symbols(self):
        """Distinct symbols in matrix"""
        symbols = set()
        [symbols.update(vals) for vals in self.matrix.values()]
        return symbols
    
    @property
    def characters(self):
        out = defaultdict(dict)
        for taxon in self.taxa:
            for index, _ in enumerate(self.matrix[taxon]):
                label = self.charlabels.get(index, index)
                out[label][taxon] = self.matrix[taxon][index]
        return out
    
    def is_missing_or_gap(self, state):
        return True if state in ('-', '?') else False
    
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
        
        line = line.lower()
        line = line.replace(" =", "=").replace("= ", "=")  # standardise
        for chunk in WHITESPACE_PATTERN.split(line):
            try:
                key, value = chunk.split("=")
                value = QUOTED_PATTERN.sub('\\1', value)
            except ValueError:
                key, value = chunk, True
            if key:
                out[key] = value
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
        sites = [s for s in sites if s not in remove_values]
        if '(' not in sites:
            return sites
        else:
            multistate = False
            out = []
            # Slow reader for multistate
            while sites:
                site = sites.pop(0)
                if site == ',':
                    continue
                elif site == '(':
                    # read-ahead
                    site = ''  # discard open bracket
                    multistate = True
                    while multistate:
                        nextchar = sites.pop(0)
                        if nextchar == ')':
                            multistate = False
                        else:
                            site += nextchar
                out.append(site)
            return out

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

    def parse(self, data):
        """
        Parses a `data` block

        :param data: data block
        :type data: string

        :return: None
        :raises NexusFormatException: If parsing fails
        :raises NotImplementedError: If parsing encounters an unknown section
        """
        super(DataHandler, self).parse(data)
        self.format = self.parse_format_line("\n".join(data))
        data = self._parse_charstate_block(data)

        _dim_taxa, _dim_chars = None, None

        seen_matrix = False
        for line in data:
            lline = line.lower().strip()
            # Dimensions line
            if lline.startswith('dimensions '):
                # try for ntaxa
                try:
                    _dim_taxa = int(NTAX_PATTERN.findall(line)[0])
                except IndexError:  # pragma: no cover
                    pass
                # and nchar
                try:
                    _dim_chars = int(NCHAR_PATTERN.findall(line)[0])
                except IndexError:  # pragma: no cover
                    pass
                    
            elif self.is_mesquite_attribute(line):
                self.attributes.append(line)
            # handle format line
            elif lline.startswith('format'):
                continue
            elif lline.startswith('matrix'):
                seen_matrix = True
                continue
            # ignore a few things..
            elif BEGIN_PATTERN.match(line):
                continue
            elif seen_matrix:
                line = self.remove_comments(line)

                # NORMALISE WHITESPACE
                try:
                    taxon, sites = WHITESPACE_PATTERN.split(line, 1)
                except ValueError:
                    continue

                taxon = QUOTED_PATTERN.sub('\\1', taxon.strip())
                self.add_taxon(taxon, self._parse_sites(sites.strip()))

        # Warn if format string (ntaxa or nchar) does not give the right answer
        if _dim_taxa is not None and self.ntaxa != _dim_taxa:
            warnings.warn(
                "Expected %d taxa, got %d" % (self.ntaxa, _dim_taxa)
            )

        if _dim_chars is not None and self.nchar != _dim_chars:
            warnings.warn(
                "Expected %d characters, got %d" % (self.nchar, _dim_chars)
            )

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
    
    def write(self):
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
        
        out = []
        out.append('begin data;')
        for att in self.attributes:
            out.append("\t%s" % att)
        out.append('\tdimensions ntax=%d nchar=%d;' % (self.ntaxa, self.nchar))
        out.append(_make_format_line(self))
        # handle char block
        if self.charlabels:
            out.append('\tcharstatelabels')
            max_id = max(self.charlabels)
            for char_id in sorted(self.charlabels):
                out.append('\t\t%d %s%s' % (
                    char_id + 1,  # zero-indexing
                    self.charlabels[char_id],
                    ',' if char_id < max_id else ''
                ))
            out.append('\t;')
        out.append("matrix")
        max_taxon_len = max([len(_) for _ in self.matrix])
        for taxon in sorted(self.matrix):
            out.append("%s %s" % (taxon.ljust(max_taxon_len), ''.join(self.matrix[taxon])))
        out.append(" ;")
        out.append("end;")
        return "\n".join(out)

    def __repr__(self):
        return "<NexusDataBlock: %d characters from %d taxa>" % \
            (self.nchar, self.ntaxa)


class CharacterHandler(DataHandler):
    pass
