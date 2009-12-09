"""
Tools for reading a nexus file
"""
import re

DEBUG = False

BEGIN_PATTERN = re.compile(r"""begin (\w+);""", re.IGNORECASE)
END_PATTERN1 = re.compile(r"""end;""", re.IGNORECASE)
END_PATTERN2 = re.compile(r"""^;$""")
NTAX_PATTERN = re.compile(r"""ntax=(\d+)""", re.IGNORECASE)
NCHAR_PATTERN = re.compile(r"""nchar=(\d+)""", re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"""(\[.*?\])""")

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
        """
        return COMMENT_PATTERN.sub('', line)
    
    
    
    
    
class TreeHandler(GenericHandler):
    """Handler for `trees` blocks"""
    is_tree = re.compile(r"""tree ([\w\d\.]+)\s\=\s(.*);""")
    
    def __init__(self):
        self.ntrees = 0
        self.trees = []
        
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
    
    def parse_format_line(self, line):
        """
        Parses a format line, and returns a dictionary of tokens
        
        >>> d = DataHandler().parse_format_line('Format datatype=standard symbols="01" gap=-;')
        >>> assert d['datatype'] == 'standard', "Expected 'standard', but got '%s'" % d['datatype']
        >>> assert d['symbols'] == '01', "Expected '01', but got '%s'" % d['symbols']
        >>> assert d['gap'] == '-', "Expected 'gap', but got '%s'" % d['gap']
        
        >>> d = DataHandler().parse_format_line('FORMAT datatype=RNA missing=? gap=- symbols="ACGU" labels interleave;')
        >>> assert d['datatype'] == 'rna', "Expected 'rna', but got '%s'" % d['datatype']
        >>> assert d['missing'] == '?', "Expected '?', but got '%s'" % d['missing']
        >>> assert d['gap'] == '-', "Expected '-', but got '%s'" % d['gap']
        >>> assert d['symbols'] == 'acgu', "Expected 'acgu', but got '%s'" % d['symbols']
        >>> assert d['labels'] == True, "Expected <True>, but got '%s'" % d['labels']
        >>> assert d['interleave'] == True, "Expected <True>, but got '%s'" % d['interleave']
        """
        out = {}
        line = line.lower()
        # cleanup
        line = line.lstrip('format').strip(';').strip().replace('"', '')
        for chunk in line.split():
            try:
                k, v = chunk.split("=")
            except ValueError:
                k, v = chunk, True
            out[k] = v
        return out
        
    def parse(self, data):
        for line in data:
            lline = line.lower().strip()
            lline = self.remove_comments(lline)
            # Dimensions line
            if lline.startswith('dimensions '):
                # try for nchar/ntax
                self.ntaxa = int(NTAX_PATTERN.findall(line)[0])
                self.nchar = int(NCHAR_PATTERN.findall(line)[0])
            
            # handle format line
            elif lline.startswith('format '):
                self.format = self.parse_format_line(line)
            elif lline.startswith('matrix'):
                seen_matrix = True
                continue
            # ignore a few things..
            elif BEGIN_PATTERN.match(line):
                continue
            elif 'charstatelabels' in lline:
                raise NotImplementedError, 'Character block parsing is not implemented yet'
            elif seen_matrix == True:
                try:
                    taxon, sites = line.split(' ', 1)
                except ValueError:
                    continue
                
                taxon = taxon.strip()
                sites = sites.strip()
                
                if taxon not in self.taxa:
                    self.taxa.append(taxon)
                
                self.matrix[taxon] = self.matrix.get(taxon, [])
                self.matrix[taxon].append(sites)
        
    def __repr__(self):
        return "<NexusDataBlock: %d characters from %d taxa>" % (self.nchar, self.ntaxa)
        

class NexusReader(object):
    known_blocks = {
        'trees': TreeHandler,
        'data': DataHandler,
    }
    
    def __init__(self, filename=None):
        self.blocks = {}
        self.rawblocks = {}
        
        if filename:
            return self.read_file(filename)
        
    def _do_blocks(self):
        for block, data in self.raw_blocks.iteritems():
            self.blocks[block] = self.known_blocks.get(block, GenericHandler)()
            self.blocks[block].parse(data)
    
    def read_file(self, filename):
        """
        Loads and Parses a Nexus File
        """
        self.filename = filename
        try:
            handle = open(filename, 'rU')
        except IOError:
            raise IOError, "Unable To Read File %s" % filename
        
        store = {}
        block = None
        for line in handle.xreadlines():
            line = line.strip()
            if len(line) == 0:
                continue
            elif line.startswith('[') and line.endswith(']'):
                continue
            
            # check if we're in a block and initialise
            found = BEGIN_PATTERN.findall(line)
            if found:
                block = found[0].lower()
                if store.has_key(block):
                    raise Exception, "Duplicate Block %s" % block
                store[block] = []
                
            # check if we're ending a block
            if END_PATTERN1.search(line) or END_PATTERN2.search(line):
                block = None
                
            if block is not None:
                store[block].append(line)
        handle.close()
        
        self.raw_blocks = store
        self._do_blocks()
        return
