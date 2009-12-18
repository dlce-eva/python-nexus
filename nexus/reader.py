"""
Tools for reading a nexus file
"""
import re
import io

DEBUG = False

BEGIN_PATTERN = re.compile(r"""begin (\w+);""", re.IGNORECASE)
END_PATTERN = re.compile(r"""end;""", re.IGNORECASE)
NTAX_PATTERN = re.compile(r"""ntax=(\d+)""", re.IGNORECASE)
NCHAR_PATTERN = re.compile(r"""nchar=(\d+)""", re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"""(\[.*?\])""")
WHITESPACE_PATTERN = re.compile(r"""\s+""")
QUOTED_PATTERN = re.compile(r"""^["'](.*)["']$""")


class NexusFormatException(Exception):
    def __init__(self, arg):
        self.value = arg
    def __str__(self):
        return repr(self.value)


class GenericHandler(object):
    def __init__(self):
        """Initialise datastore in <storage> under <keyname>"""
        self.storage = []
        
    def parse(self, data):
        for line in data:
            self.storage.append(line)
            
    def remove_comments(self, line):
        """
        Removes comments from lines
        
        >>> g = GenericHandler()
        >>> g.remove_comments("Hello [world]")
        'Hello '
        >>> g.remove_comments("He[bite]ll[me]o")
        'Hello'
        
        :param line: string
        :type line: string
        
        :return: Returns a cleaned string.
        """
        return COMMENT_PATTERN.sub('', line)
    
    
class TaxaHandler(GenericHandler):
    """Handler for `taxa` blocks"""
    is_dimensions = re.compile(r"""dimensions ntax=(\d+)""", re.IGNORECASE)
    is_taxlabel_block = re.compile(r"""\btaxlabels\b""", re.IGNORECASE)
    
    def __init__(self):
        self.taxa = []
    
    def __getitem__(self, index):
        return self.taxa[index]
        
    def parse(self, data):
        in_taxlabel_block = False
        for line in data:
            line = self.remove_comments(line).strip()
            line = QUOTED_PATTERN.sub('\\1', line)
            if self.is_dimensions.match(line):
                self.ntaxa = int(self.is_dimensions.findall(line)[0])
            elif line == ';':
                continue
            elif self.is_taxlabel_block.match(line):
                in_taxlabel_block = True
            elif in_taxlabel_block:
                self.taxa.append(line)
        assert self.ntaxa == len(self.taxa)

class TreeHandler(GenericHandler):
    """Handler for `trees` blocks"""
    is_tree = re.compile(r"""tree ([\w\d\.]+)\s\=\s(.*);""")
    
    def __init__(self):
        self.ntrees = 0
        self.trees = []
        
    def __getitem__(self, index):
        return self.trees[index]
        
    def parse(self, data):
        for line in data:
            if self.is_tree.search(line):
                self.trees.append(line)
                self.ntrees += 1
                
    def __repr__(self):
        return "<NexusTreeBlock: %d trees>" % self.ntrees
         
        
        
class DataHandler(GenericHandler):
    """Handler for data matrices"""
    def __init__(self):
        self.taxa = []
        self.ntaxa = 0
        self.nchar = 0
        self.format = {}
        self.gaps = None
        self.missing = None
        self.matrix = {}
    
    def __getitem__(self, index):
        return (self.taxa[index], self.matrix[self.taxa[index]])
    
    def parse_format_line(self, data):
        """
        Parses a format line, and returns a dictionary of tokens
        
        >>> d = DataHandler().parse_format_line('Format datatype=standard symbols="01" gap=-;')
        ...
        >>> d = DataHandler().parse_format_line('FORMAT datatype=RNA missing=? gap=- symbols="ACGU" labels interleave;')
        ...
        
        :param data: string
        :type data: string
        
        :return: Returns a dictionary of tokens in the format line.
        """
        out = {}
        
        try:
            line = re.findall(r'format\b(.*?);', data, re.IGNORECASE | re.DOTALL | re.MULTILINE)[0]
        except IndexError:
            return None
        
        line = line.strip(';')
        line = line.lower()
        
        for chunk in WHITESPACE_PATTERN.split(line):
            try:
                k, v = chunk.split("=")
                v = QUOTED_PATTERN.sub('\\1', v)
            except ValueError:
                k, v = chunk, True
            if len(k):
                out[k] = v
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
        
        :param sites: string
        :type sites: string
        
        :return: Returns a list of site values
        :raises NexusFormatException: If data matrix contains incomplete multistate values
        """
        out = []
        multistate = False
        sites = [s for s in sites]
        while len(sites) > 0:
            s = sites.pop(0)
            if s == '(':
                # read-ahead
                s = '' # discard open bracket
                multistate = True
                while multistate:
                    t = sites.pop(0)
                    if t == ')':
                        multistate = False
                    else:
                        s += t
            out.append(s)
        # check we're not in hanging multistate chunk
        if multistate:
            raise NexusFormatException("Data Matrix contains incomplete multistate values")
        return out
        
        
    def parse(self, data):
        """
        Parses a `data` block
        
        :param data: data block 
        :type data: string
        
        :return: None
        :raises NexusFormatException: If parsing fails
        :raises NotImplementedError: If parsing encounters a not implemented section
        """        
        seen_matrix = False
        self.format = self.parse_format_line("\n".join(data))
        
        for line in data:
            lline = line.lower().strip()
            lline = self.remove_comments(lline)
            # Dimensions line
            if lline.startswith('dimensions '):
                # try for nchar/ntax
                try:
                    self.ntaxa = int(NTAX_PATTERN.findall(line)[0])
                except IndexError:
                    self.ntaxa = None
                
                self.nchar = int(NCHAR_PATTERN.findall(line)[0])
                
            # handle format line
            elif lline.startswith('format'):
                continue
            elif lline.startswith('matrix'):
                seen_matrix = True
                continue
            # ignore a few things..
            elif BEGIN_PATTERN.match(line):
                continue
            elif 'charstatelabels' in lline:
                raise NotImplementedError('Character block parsing is not implemented yet')
            elif seen_matrix == True:
                # NORMALISE WHITESPACE
                try:
                    taxon, sites = WHITESPACE_PATTERN.split(line, 1)
                except ValueError:
                    continue
                taxon = taxon.strip()
                taxon = QUOTED_PATTERN.sub('\\1', taxon)
                sites = sites.strip()
                
                if taxon not in self.taxa:
                    self.taxa.append(taxon)
                
                self.matrix[taxon] = self.matrix.get(taxon, [])
                self.matrix[taxon].extend(self._parse_sites(sites))
            
        if self.ntaxa is None:
            self.ntaxa = len(self.taxa)
        
    def __repr__(self):
        return "<NexusDataBlock: %d characters from %d taxa>" % (self.nchar, self.ntaxa)
        

class NexusReader(object):
    known_blocks = {
        'data': DataHandler,
        'characters': DataHandler,
        'trees': TreeHandler,
        'taxa': TaxaHandler,
    }
    
    def __init__(self, filename=None, debug=False):
        self.debug = debug
        self.blocks = {}
        self.rawblocks = {}
        
        if filename:
            return self.read_file(filename)
        
    def _do_blocks(self):
        for block, data in self.raw_blocks.items():
            if block == 'characters':
                block = 'data' # override
            self.blocks[block] = self.known_blocks.get(block, GenericHandler)()
            self.blocks[block].parse(data)
            setattr(self, block, self.blocks[block])
        
    def read_file(self, filename):
        """Loads and Parses a Nexus File"""
        self.filename = filename
        try:
            handle = open(filename, 'rU')
        except IOError:
            raise IOError("Unable To Read File %s" % filename)
        self._read(handle)
        handle.close()
        
    def read_string(self, contents):
        """Loads and Parses a Nexus from a string"""
        self._read(io.StringIO(contents))
        
    def _read(self, handle):
        """Reads from a iterable object"""
        store = {}
        block = None
        for line in handle.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            elif line.startswith('[') and line.endswith(']'):
                continue
            
            # check if we're in a block and initialise
            found = BEGIN_PATTERN.findall(line)
            if found:
                block = found[0].lower()
                if block in store:
                    raise Exception("Duplicate Block %s" % block)
                store[block] = []
                
            # check if we're ending a block
            if END_PATTERN.search(line):
                block = None
                
            if block is not None:
                store[block].append(line)
        self.raw_blocks = store
        self._do_blocks()
