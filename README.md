# python-nexus

A Generic nexus (.nex, .trees) reader/writer for python.

[![Build Status](https://github.com/dlce-eva/python-nexus/workflows/tests/badge.svg)](https://github.com/dlce-eva/python-nexus/actions?query=workflow%3Atests)
[![codecov](https://codecov.io/gh/dlce-eva/python-nexus/branch/master/graph/badge.svg)](https://codecov.io/gh/dlce-eva/python-nexus)
[![PyPI](https://img.shields.io/pypi/v/python-nexus.svg)](https://pypi.org/project/python-nexus)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.595426.svg)](https://doi.org/10.5281/zenodo.595426)


## Description

python-nexus provides simple nexus file-format reading/writing tools, and a small
collection of nexus manipulation scripts.

Note: Due to a name clash with another python package, this package must be **installed** as
`pip install python-nexus` but **imported** as `import nexus`.


## Usage

### CLI

`python-nexus` installs a command `nexus` for cli use. You can inspect its help via
```shell
nexus -h
```

### Python API

Reading a Nexus:
```python
>>> from nexus import NexusReader
>>> n = NexusReader.from_file('tests/examples/example.nex')
```    

You can also load from a string:
```python
>>> n = NexusReader.from_string('#NEXUS\n\nbegin foo; ... end;')
```

NexusReader will load each of the nexus `blocks` it identifies using specific `handlers`. 
```python
>>> n.blocks
{'foo': <nexus.handlers.GenericHandler object at 0x7f55d94140f0>}
>>> n = NexusReader('tests/examples/example.nex')
>>> n.blocks
{'data': <NexusDataBlock: 2 characters from 4 taxa>}
```

A dictionary mapping blocks to handlers is available as `nexus.reader.HANDLERS:
```python
>>> from nexus.reader import HANDLERS
>>> HANDLERS
{
    'trees': <class 'nexus.handlers.tree.TreeHandler'>, 
    'taxa': <class 'nexus.handlers.taxa.TaxaHandler'>, 
    'characters': <class 'nexus.handlers.data.CharacterHandler'>, 
    'data': <class 'nexus.handlers.data.DataHandler'>
}
```

Any blocks that aren't in this dictionary will be parsed using `nexus.handlers.GenericHandler`.

`NexusReader` can then write the nexus to a string using `NexusReader.write` or to another 
file using `NexusReader.write_to_file`:
```python
>>> output = n.write()
>>> n.write_to_file("mynewnexus.nex")
```

Note: if you want more fine-grained control over generating nexus files, then try
`NexusWriter` discussed below.


### Block Handlers:

There are specific "Handlers" to parse certain known nexus blocks, including the
common 'data', 'trees', and 'taxa' blocks. Any blocks that are unknown will be 
parsed with GenericHandler.

ALL handlers extend the `GenericHandler` class and have the following methods.

* `__init__(self, name=None, data=None)`
    `__init__` is called by `NexusReader` to parse the contents of the block (in `data`)
    appropriately.

* `write(self)`
    write is called by `NexusReader` to write the contents of a block to a string 
    (i.e. for regenerating the nexus format for saving a file to disk)



#### `generic` block handler

The generic block handler simply stores each line of the block in `.block`:

    n.blockname.block
    ['line1', 'line2', ... ]


#### `data` block handler

These are the main blocks encountered in nexus files - and contain the data matrix.

So, given the following nexus file with a data block:

    #NEXUS 
    
    Begin data;
    Dimensions ntax=4 nchar=2;
    Format datatype=standard symbols="01" gap=-;
        Matrix
    Harry              00
    Simon              01
    Betty              10
    Louise             11
        ;
    End;
    
    begin trees;
        tree A = ((Harry:0.1,Simon:0.2),Betty:0.2)Louise:0.1;;
        tree B = ((Simon:0.1,Harry:0.2),Betty:0.2)Louise:0.1;;
    end;


You can do the following:

Find out how many characters:
```python
>>> n.data.nchar
2
```

Ask about how many taxa:
```python
>>> n.data.ntaxa
4
```

Get the taxa names:
```python 
>>> n.data.taxa
['Harry', 'Simon', 'Betty', 'Louise']
```

Get the `format` info:
```python 
>>> n.data.format
{'datatype': 'standard', 'symbols': '01', 'gap': '-'}
```

The actual data matrix is a dictionary, which you can get to in `.matrix`:
```python
>>> n.data.matrix
defaultdict(<class 'list'>, {'Harry': ['0', '0'], 'Simon': ['0', '1'], 'Betty': ['1', '0'], 'Louise': ['1', '1']})
```

Or, you could access the data matrix via taxon:
```python
>>> n.data.matrix['Simon']
['0', '1']
```    

Or even loop over it like this:
```python
>>> for taxon, characters in n.data:
...     print(taxon, characters)
...     
Harry ['0', '0']
Simon ['0', '1']
Betty ['1', '0']
Louise ['1', '1']
```

You can also iterate over the sites (rather than the taxa):
```python
>>> for site, data in n.data.characters.items():
...     print(site, data)
...     
0 {'Harry': '0', 'Simon': '0', 'Betty': '1', 'Louise': '1'}
1 {'Harry': '0', 'Simon': '1', 'Betty': '0', 'Louise': '1'}
```

..or you can access the characters matrix directly:
```python
>>> n.data.characters[0]
{'Harry': '0', 'Simon': '0', 'Betty': '1', 'Louise': '1'}

```

Note: that sites are zero-indexed!

#### `trees` block handler

If there's a `trees` block, then you can do the following

You can get the number of trees:
```python
>>> n.trees.ntrees
2
```

You can access the trees via the `.trees` dictionary:
```python
>>> n.trees.trees[0]
'tree A = ((Harry:0.1,Simon:0.2):0.1,Betty:0.2):Louise:0.1);'
```

Or loop over them:
```python
>>> for tree in n.trees:
...     print(tree)
... 
tree A = ((Harry:0.1,Simon:0.2):0.1,Betty:0.2):Louise:0.1);
tree B = ((Simon:0.1,Harry:0.2):0.1,Betty:0.2):Louise:0.1);
```

For further inspection of trees via  the [newick package](https://pypi.org/project/newick/), you can retrieve 
a `nexus.Node` object for a tree:
```python
>>> print(n.trees.trees[0].newick_tree.ascii_art())
                  ┌─Harry
         ┌────────┤
──Louise─┤        └─Simon
         └─Betty

```


#### `taxa` block handler

Programs like SplitsTree understand "TAXA" blocks in Nexus files:

    BEGIN Taxa;
    DIMENSIONS ntax=4;
    TAXLABELS
    [1] 'John'
    [2] 'Paul'
    [3] 'George'
    [4] 'Ringo'
    ;
    END; [Taxa]


In a taxa block you can get the number of taxa and the taxa list:
```python
>>> n.taxa.ntaxa
4
>>> n.taxa.taxa
['John', 'Paul', 'George', 'Ringo']
```

NOTE: with this alternate nexus format the Characters blocks *should* be parsed by
DataHandler.


### Writing a Nexus File using NexusWriter


`NexusWriter` provides more fine-grained control over writing nexus files, and 
is useful if you're programmatically generating a nexus file rather than loading
a pre-existing one.
```python
>>> from nexus import NexusWriter
>>> n = NexusWriter()
>>> #Add a comment to appear in the header of the file
>>> n.add_comment("I am a comment")
```

Data are added by using the "add" function - which takes 3 arguments, a taxon, 
a character name, and a value.
```python
>>> n.add('taxon1', 'Character1', 'A')
>>> n.data
{'Character1': {'taxon1': 'A'}}
>>> n.add('taxon2', 'Character1', 'C')
>>> n.add('taxon3', 'Character1', 'A')
```

Characters and values can be strings or integers (but you **cannot** mix string and
integer characters).
```python
>>> n.add('taxon1', 2, 1)
>>> n.add('taxon2', 2, 2)
>>> n.add('taxon3', 2, 3)
```

NexusWriter will interpolate missing entries (i.e. taxon2 in this case)
```python
>>> n.add('taxon1', "Char3", '4')
>>> n.add('taxon3', "Char3", '4')
```

... when you're ready, you can generate the nexus using `make_nexus` or `write_to_file`:
```python    
>>> data = n.make_nexus(interleave=True, charblock=True)
>>> n.write_to_file(filename="output.nex", interleave=True, charblock=True)
```

... you can make an interleaved nexus by setting `interleave` to True, and you can
include a character block in the nexus (if you have character labels for example) 
by setting charblock to True.

There is rudimentary support for handling trees e.g.:
```python
>>> n.trees.append("tree tree1 = (a,b,c);")
>>> n.trees.append("tree tree2 = (a,b,c);")
```