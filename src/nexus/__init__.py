"""
python-nexus - Generic nexus (.nex, .trees) reader for python
=============================================================

Reading a Nexus
---------------

>>> import os
>>> EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'examples')
>>>
>>> from nexus import NexusReader
>>> n = NexusReader.from_file(os.path.join(EXAMPLE_DIR, 'example.nex'))
...

# display blocks found in data file
>>> n.blocks
{'data': <NexusDataBlock: 2 characters from 4 taxa>}

`data` blocks
-------------

>>> n.data.nchar
2

>>> n.data.ntaxa
4

>>> n.data.format
{'datatype': 'standard', 'symbols': '01', 'gap': '-'}

>>> n.data.matrix.keys()
['Simon', 'Louise', 'Betty', 'Harry']

>>> n.data.matrix['Simon']
['0', '1']

>>> sorted(n.data.taxa)
['Betty', 'Harry', 'Louise', 'Simon']

>>> sorted(n.data.matrix.keys())
['Betty', 'Harry', 'Louise', 'Simon']

>>> for taxon, characters in n.data: #doctest: +SKIP


`tree` blocks
-------------

>>> n = NexusReader.from_file(os.path.join(EXAMPLE_DIR, 'example.trees'))
>>> n.trees.ntrees
3
>>> n.trees.trees[0][0:60]
'tree tree.0.1065.603220 = (((((((Chris:0.0668822155,Bruce:0.'

>>> for tree in n.trees: #doctest: +SKIP



Writing a Nexus File
--------------------
>>> from nexus import NexusWriter
>>> n = NexusWriter()

Add a comment to appear in the header of the file
>>> n.add_comment("I am a comment")

data are added by using the "add" function -
which takes 3 arguments, a taxon, a character name, and a value

>>> n.add('taxon1', 'Character1', 'A')
>>> n.data
{'Character1': {'taxon1': 'A'}}
>>> n.add('taxon2', 'Character1', 'C')
>>> n.add('taxon3', 'Character1', 'A')

Characters and values can be strings or integers
>>> n.add('taxon1', 2, 1)
>>> n.add('taxon2', 2, 2)
>>> n.add('taxon3', 2, 3)

NexusWriter will interpolate missing entries (i.e. taxon2 in this case)
>>> n.add('taxon1', "Char3", '4')
>>> n.add('taxon3', "Char3", '4')

... when you're ready, you can generate the nexus using `make_nexus`
or `write_to_file`:
n.make_nexus(interleave=True, charblock=True)
n.write_to_file(filename="output.nex", interleave=True, charblock=True)

"""
from nexus.reader import NexusReader
from nexus.writer import NexusWriter
from nexus import handlers
from nexus.exceptions import NexusFormatException
from nexus import tools

__version__ = "2.1.0"
__all__ = ["NexusReader", "NexusWriter", "NexusFormatException", "handlers", "tools"]
