"""
python-nexus - Generic nexus (.nex, .trees) reader for python
=============================================================

Reading a Nexus
---------------

>>> import os
>>> EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'examples')
>>>
>>> from nexus import NexusReader
>>> n = NexusReader()
>>> n.read_file(os.path.join(EXAMPLE_DIR, 'example.nex'))
...
>>> n = NexusReader(os.path.join(EXAMPLE_DIR, 'example.nex'))
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

>>> n.data.matrix
{'Simon': ['0', '1'], 'Louise': ['1', '1'], 'Betty': ['1', '0'], 'Harry': ['0', '0']}

>>> n.data.matrix['Simon']
['0', '1']

>>> sorted(n.data.taxa)
['Betty', 'Harry', 'Louise', 'Simon']

>>> sorted(n.data.matrix.keys())
['Betty', 'Harry', 'Louise', 'Simon']

>>> for taxon, characters in n.data: #doctest: +SKIP


`tree` blocks
-------------

>>> n = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
>>> n.trees.ntrees
3
>>> n.trees.trees[0]
'tree tree.0.1065.603220 = (((((((Chris:0.0668822155,Bruce:0.0173144449):0.0062091603,Tom:0.0523825242):0.0206190840,(Henry:0.0482653647,Timothy:0.0744964092):0.0183093750):0.0401805957,(Mark:0.0066961591,Simon:0.0755275882):0.0264078188):0.0536464636,((Fred:0.0428499135,Kevin:0.0734738565):0.0937536292,Roger:0.0538708492):0.0438297939):0.0453008384,(Michael:0.0953237112,Andrew:0.0654710419):0.0803079594):0.0630363263,David:0.0855948485);'

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

... when you're ready, you can generate the nexus using `make_nexus` or `write_to_file`:
n.make_nexus(interleave=True, charblock=True)
n.write_to_file(filename="output.nex", interleave=True, charblock=True)

"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

from reader import NexusReader
from writer import NexusWriter


