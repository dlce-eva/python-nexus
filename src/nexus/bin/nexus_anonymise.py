#!/usr/bin/env python
import sys
import hashlib
from nexus import VERSION
from nexus.reader import NexusReader

__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexus_anonymise - python-nexus tools v%(version)s

Anonymises the taxa in a nexus
""" % {'version': VERSION, }


def anonymise(nexus_obj, salt=None):
    """Anonymises a nexus object"""
    _done_data = False  # flag so we don't double randomise
    for block in nexus_obj.blocks:
        if block == 'taxa':
            for idx, t in enumerate(nexus_obj.blocks[block].taxa):
                nexus_obj.blocks[block].taxa[idx] = hash(salt, t)
        elif block == 'trees':
            if nexus_obj.blocks[block].was_translated:
                for idx in nexus_obj.blocks[block].translators:
                    h = hash(
                        salt,
                        nexus_obj.blocks[block].translators[idx]
                    )
                    nexus_obj.blocks[block].translators[idx] = h
            else:
                raise NotImplementedError(
                    "Unable to anonymise untranslated trees"
                )
        elif block in ('data', 'characters'):
            if _done_data:
                continue
            newmatrix = {}
            for t in nexus_obj.blocks[block].matrix:
                newmatrix[hash(salt, t)] = nexus_obj.blocks[block].matrix[t]
            nexus_obj.blocks[block].matrix = newmatrix
            
            if block == 'characters':
                nexus_obj.blocks['data'].matrix = newmatrix
            _done_data = True
        else:
            raise NotImplementedError("Unable to anonymise `%s` blocks" % block)
    return nexus_obj


def hash(salt, value):
    return hashlib.md5(("%s-%s" % (salt, value)).encode('ascii')).hexdigest()


if __name__ == '__main__':  # pragma: no cover
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog fudge.nex output.nex")
    options, args = parser.parse_args()

    try:
        nexusname = args[0]
    except IndexError:
        print(__doc__)
        print("Author: %s\n" % __author__)
        parser.print_help()
        sys.exit()

    try:
        newnexus = args[1]
    except IndexError:
        newnexus = None

    nexus = NexusReader(nexusname)
    nexus = anonymise(nexus)

    if newnexus is not None:
        nexus.write_to_file(newnexus)
        print("New nexus written to %s" % newnexus)
    else:
        print(nexus.write_to_file(hash('filename', nexusname)))
