"""
python-nexus - Generic nexus (.nex) reader for python
=====================================================

Reading a Nexus
---------------
>>> from reader import Nexus
>>> nex = Nexus()
>>> nex.read_file('examples/example.nex')
...
>>> nex = Nexus('examples/example.nex')
...

# display blocks found in data file
>>> nex.blocks
{'data': <NexusDataBlock: 2 characters from 4 taxa>}

`data` blocks
-------------

>>> nex.blocks['data'].nchar
2

>>> nex.blocks['data'].ntaxa
4

>>> nex.blocks['data'].matrix
{'Simon': ['01'], 'Louise': ['11'], 'Betty': ['10'], 'Harry': ['00']}

>>> nex.blocks['data'].matrix['Simon']
['01']

>>> sorted(nex.blocks['data'].taxa)
['Betty', 'Harry', 'Louise', 'Simon']

>>> sorted(nex.blocks['data'].matrix.keys())
['Betty', 'Harry', 'Louise', 'Simon']


`tree` blocks
-------------

>>> nex.read_file('examples/example.trees')
>>> nex.blocks['trees'].ntrees
3
>>> nex.blocks['trees'].trees[0]
'tree tree.0.1065.603220 = (((((((Chris:0.0668822155,Bruce:0.0173144449):0.0062091603,Tom:0.0523825242):0.0206190840,(Henry:0.0482653647,Timothy:0.0744964092):0.0183093750):0.0401805957,(Mark:0.0066961591,Simon:0.0755275882):0.0264078188):0.0536464636,((Fred:0.0428499135,Kevin:0.0734738565):0.0937536292,Roger:0.0538708492):0.0438297939):0.0453008384,(Michael:0.0953237112,Andrew:0.0654710419):0.0803079594):0.0630363263,David:0.0855948485);'




Parsing specific blocks
-----------------------

Class Nexus is a generic object for loading nexus information.

The Handlers are objects to store specialised blocks found in nexus files, and 
are initialised in Nexus.known_blocks: 

    Nexus.known_blocks = {
        'trees': TreeHandler,
        'data': DataHandler,
    }
    
    ...adding a specialised handler for a certain block type is as easy as subclassing GenericHandler,
    and attaching it into the Nexus known_blocks dictionary under the block label, e.g.
    
    n = Nexus()
    n.known_blocks['r8s'] = R8sBlockHandler
    n.read_file('myfile.nex')
    print n.blocks['r8s']
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'
