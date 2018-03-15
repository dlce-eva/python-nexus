"""
Tools for reading a nexus file
"""
import os
import gzip

try:  # pragma: no cover
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from nexus.handlers import GenericHandler
from nexus.handlers import BEGIN_PATTERN, END_PATTERN
from nexus.handlers.taxa import TaxaHandler
from nexus.handlers.data import CharacterHandler, DataHandler
from nexus.handlers.tree import TreeHandler
from nexus.exceptions import NexusFormatException


class NexusReader(object):
    """A nexus reader"""
    def __init__(self, filename=None, debug=False):
        self.debug = debug
        self.blocks = {}
        self.raw_blocks = {}
        self.handlers = {
            'data': DataHandler,
            'characters': CharacterHandler,
            'trees': TreeHandler,
            'taxa': TaxaHandler,
        }
        if filename:
            self.read_file(filename)

    def _do_blocks(self):
        """Iterates over all nexus blocks and parses them appropriately"""
        for block, data in self.raw_blocks.items():
            self.blocks[block] = self.handlers.get(block, GenericHandler)()
            self.blocks[block].parse(data)
        
        if self.blocks.get('characters') and not self.blocks.get('data'):
            self.blocks['data'] = self.blocks['characters']
        
        for block in self.blocks:
            setattr(self, block, self.blocks[block])
        
    def read_file(self, filename):
        """
        Loads and Parses a Nexus File

        :param filename: filename of a nexus file
        :type filename: string

        :raises IOError: If file reading fails.

        :return: None
        """
        self.filename = filename
        self.short_filename = os.path.split(filename)[1]

        if not os.path.isfile(filename):
            raise IOError("Unable To Read File %s" % filename)

        if filename.endswith('.gz'):
            handle = gzip.open(filename, 'rb')  # pragma: no cover
        else:
            handle = open(filename, 'r')
        self._read(handle)
        handle.close()

    def read_string(self, contents):
        """
        Loads and Parses a Nexus from a string

        :param contents: string or string-like object containing a nexus
        :type contents: string

        :return: None
        """
        self.filename = "<String>"
        self._read(StringIO(contents))
        return self
        
    def _read(self, handle):
        """Reads from a iterable object"""
        store = {}
        block = None
        for line in handle.readlines():
            if hasattr(line, 'decode'):
                line = line.decode('utf-8')
            line = line.strip()
            if not line:
                continue
            elif line.startswith('[') and line.endswith(']'):
                continue

            # check if we're in a block and initialise
            found = BEGIN_PATTERN.findall(line)
            if found:
                block = found[0][0].lower()
                if block in store:
                    raise NexusFormatException("Duplicate Block %s" % block)
                store[block] = []

            # check if we're ending a block
            if END_PATTERN.search(line):
                block = None

            if block is not None:
                store[block].append(line)
        self.raw_blocks = store
        self._do_blocks()

    def write(self):
        """
        Generates a string containing a complete nexus from
        all the data.

        :return: String
        """
        out = ["#NEXUS\n"]
        for block in self.blocks:
            out.append(self.blocks[block].write())
        return "\n".join(out)

    def write_to_file(self, filename):
        """
        Writes the nexus to a file.

        :return: None

        :raises IOError: If file writing fails.
        """
        handle = open(filename, 'w')
        handle.writelines(self.write())
        handle.close()
