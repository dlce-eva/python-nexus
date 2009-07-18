#!/usr/bin/env python
"""
Generic nexus (.nex) reader for python

>>> n = Nexus(filename)
>>> 

"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import re
  
BEGIN_PATTERN = re.compile(r"""begin (\w+);""", re.IGNORECASE)
END_PATTERN1 = re.compile(r"""end;""", re.IGNORECASE)
END_PATTERN2 = re.compile(r"""^;$""")
NTAX_PATTERN = re.compile(r"""NTAX=(\d+)""", re.IGNORECASE)
NCHAR_PATTERN = re.compile(r"""NCHAR=(\d+)""", re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"""(\[.*\])""")

class GenericHandler(object):
    data = []
    
    def __init__(self):
        pass
        
    def parse_line(self, line):
        self.data.append(line)
    
class TreeHandler(GenericHandler):
    def parse_line(self, line):
        raise NotImplementedError
        


class Nexus(object):
    nexus = {}
    
    known_blocks = {
        'trees': TreeHandler,
    }
    
    
    def __init__(self, filename):
        self.filename = filename
        self.read_file(self.filename)
    
    
    def read_file(self, filename):
        """
        Loads and Parses a Nexus File
        """
        try:
            handle = open(filename, 'rU')
        except IOError:
            raise IOError, "Unable To Read File %s" % input
        
        block, handler = None, None
        for line in handle.xreadlines():
            
            line = line.strip()
            if len(line) == 0:
                continue
            # nuke comments
            if '[' in line:
                line = COMMENT_PATTERN.sub('', line)
                
            # check if we're in a block and initialise
            found = BEGIN_PATTERN.findall(line)
            if found:
                block = found[0].lower()
                if self.nexus.has_key(block):
                    raise Exception, "Duplicate Block %s" % block
                handler = self.known_blocks.get(block, GenericHandler)()
                #self.nexus[block] = 
                
            # check if we're ending a block
            if END_PATTERN1.search(line) or END_PATTERN2.search(line):
                block, handler = None, None
                
            if block is not None and handler is not None:
                handler.parse_line(line)
            
            
        handle.close()
        return

        
    
if __name__ == '__main__':
    n = Nexus('examples/bees.nex')
    for k, v in n.nexus.iteritems():
        print k
        print v
        print
        
    