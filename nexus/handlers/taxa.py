import re
from nexus.handlers import GenericHandler, NexusFormatException
from nexus.handlers import QUOTED_PATTERN


class TaxaHandler(GenericHandler):
    """Handler for `taxa` blocks"""
    is_dimensions = re.compile(
        r"""dimensions\s*ntax\s*=\s*(\d+)""", re.IGNORECASE
    )
    is_taxlabel_block = re.compile(
        r"""\btaxlabels\b""", re.IGNORECASE
    )

    def __init__(self):
        self.taxa = []
        self.attributes = []
        super(TaxaHandler, self).__init__()

    def __getitem__(self, index):
        return self.taxa[index]

    @property
    def ntaxa(self):
        return len(self.taxa)

    def parse(self, data):
        """
        Parses a `taxa` nexus block from `data`.

        :param data: nexus block data
        :type data: string

        :return: None
        """
        super(TaxaHandler, self).parse(data)
        in_taxlabel_block = False
        found_ntaxa = None
        for line in data:
            line = self.remove_comments(line).strip()
            line = QUOTED_PATTERN.sub('\\1', line)
            if self.is_dimensions.match(line):
                found_ntaxa = int(self.is_dimensions.findall(line)[0])
            elif 'begin taxa' in line.lower():
                continue
            elif line == ';':
                continue
            elif in_taxlabel_block or self.is_taxlabel_block.match(line):
                in_taxlabel_block = True
                line = self.is_taxlabel_block.sub("", line)
                taxa = [t.replace(";", "").strip() for t in line.split(" ")]
                taxa = [t for t in taxa if t and t not in self.taxa]
                if taxa:
                    self.taxa.extend(taxa)
            elif self.is_mesquite_attribute(line):
                self.attributes.append(line)
            else:
                taxa = [t.replace(";", "").strip() for t in line.split(" ")]
                taxa = [t for t in taxa if t and t not in self.taxa]
                if taxa:
                    self.taxa.extend(taxa)
        
        if found_ntaxa and found_ntaxa != self.ntaxa:
            raise NexusFormatException(
                "Number of taxa (%d) doesn't match dimensions declaration (%d)" % (self.ntaxa, found_ntaxa)
            )


    def write(self):
        """
        Generates a string containing a taxa block for this data.

        :return: String
        """
        out = ['begin taxa;']
        # handle any attributes
        for att in self.attributes:
            out.append("\t%s" % att)
        out.append('\tdimensions ntax=%d;' % self.ntaxa)
        out.append('\ttaxlabels')
        # taxa labels
        for idx, taxon in enumerate(self.taxa, 1):
            out.append("\t[%d] '%s'" % (idx, taxon))
        out.append(';')
        out.append('end;')
        return "\n".join(out)

    def __repr__(self):
        return "<NexusTaxaBlock: %d taxa>" % self.ntaxa

