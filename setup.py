#!/usr/bin/env python
from setuptools import setup
from nexus import __version__ as version
from nexus import __doc__ as long_desc

setup(
    name="python-nexus",
    version=version,
    description="A nexus (phylogenetics) file reader (.nex, .trees)",
    long_description=long_desc,
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
    ],
    keywords="phylogenetics nexus newick paup splitstree",
    author="Simon Greenhill",
    author_email="simon@simon.net.nz",
    url="http://simon.net.nz/articles/python-nexus",
    license="BSD",
    packages=['nexus', 'nexus.tools'],
    package_dir={'nexus': 'nexus'},
    package_data={'nexus/examples': ['*.nex', '*.trees']},
    test_suite="nexus.test.nexus_suite",
    scripts=[
        'nexus/bin/nexus_anonymise.py',
        'nexus/bin/nexus_binary2multistate.py',
        'nexus/bin/nexus_combine_nexus.py',
        'nexus/bin/nexus_deinterleave.py',
        'nexus/bin/nexus_describecharacter.py',
        'nexus/bin/nexus_describetaxa.py',
        'nexus/bin/nexus_multistate2binary.py',
        'nexus/bin/nexus_nexusmanip.py',
        'nexus/bin/nexus_randomise.py',
        'nexus/bin/nexus_tally.py',
        'nexus/bin/nexus_to_fasta.py',
        'nexus/bin/nexus_treemanip.py',
    ],
)

