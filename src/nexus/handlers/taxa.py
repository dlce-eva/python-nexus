import re

from nexus.exceptions import NexusFormatException
from nexus.handlers import GenericHandler
from nexus.handlers import QUOTED_PATTERN, END_PATTERN

TAXON_PLACEHOLDER = re.compile(r"""^\[.*\]\s+""")
TAXON_ANNOTATION = re.compile(r"""(.*)(\[.*\])$""")


class TaxaHandler(GenericHandler):
    """Handler for `taxa` blocks"""
    is_dimensions = re.compile(r"""dimensions\s*ntax\s*=\s*(\d+)""", re.IGNORECASE)
    is_taxlabel_block = re.compile(r"""\btaxlabels\b""", re.IGNORECASE)

    def __init__(self, **kw):
        super(TaxaHandler, self).__init__(**kw)
        self.taxa = []
        self.attributes = []
        self.annotations = {}

        in_taxlabel_block = False
        found_ntaxa = None
        for line in self.block:
            line = QUOTED_PATTERN.sub('\\1', line)
            if self.is_dimensions.match(line):
                found_ntaxa = int(self.is_dimensions.findall(line)[0])
                continue
            elif 'begin taxa' in line.lower():
                continue
            elif line == ';' or END_PATTERN.match(line.strip()):
                continue
            elif self.is_mesquite_attribute(line):
                self.attributes.append(line)
                continue
            elif in_taxlabel_block or self.is_taxlabel_block.match(line):
                in_taxlabel_block = True
                line = self.is_taxlabel_block.sub("", line)

            for taxon, annot in self._parse_taxa(line):
                self.taxa.append(taxon)
                if annot:
                    self.annotations[taxon] = annot

        if found_ntaxa and found_ntaxa != self.ntaxa:
            raise NexusFormatException(
                "Number of found taxa (%d) doesn't match dimensions declaration (%d)" % (
                    self.ntaxa, found_ntaxa))

    def __getitem__(self, index):
        return self.taxa[index]

    @property
    def ntaxa(self):
        return len(self.taxa)

    def _parse_taxa(self, line):
        taxa = [t.replace(";", "").strip() for t in line.split(" ")]
        for taxon in taxa:
            # remove initial comment
            taxon = TAXON_PLACEHOLDER.sub('', taxon)
            # get annotations
            annot = TAXON_ANNOTATION.match(taxon)
            if annot:
                taxon, annot = annot.groups()
            # remove quotes
            taxon = QUOTED_PATTERN.sub('\\1', taxon)

            if taxon and taxon not in self.taxa:
                yield (taxon, annot)

    def iter_lines(self):
        def wrap(s):
            return s if ' ' not in s else "'%s'" % s

        for att in self.attributes:
            yield "\t%s" % att
        yield '\tdimensions ntax=%d;' % self.ntaxa
        yield '\ttaxlabels'
        # taxa labels
        for idx, taxon in enumerate(self.taxa, 1):
            taxon = "%s%s" % (taxon, self.annotations.get(taxon, ''))
            yield "\t[%d] %s" % (idx, wrap(taxon))
        yield ';'
