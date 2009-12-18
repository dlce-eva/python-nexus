from setuptools import setup, find_packages
version = "0.5"

setup(
    name="python-nexus", 
    version=version,
    description="A generic nexus (phylogenetics) file format (.nex, .trees) reader for python",
    classifiers=[
        "Programming Language :: Python", 
        "Intended Audience :: Science/Research", 
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="phylogenetics nexus newick paup splitstree",
    author="Simon Greenhill",
    author_email="simon@simon.net.nz",
    url="http://simon.net.nz/python-nexus",
    license="BSD",
    packages=['nexus'],
    package_dir={'nexus': 'nexus'},
    package_data={'nexus/examples': ['*.nex', '*.trees']},
    scripts=[
        'nexus/bin/calc_missings.py', 
        'nexus/bin/remove_constantchars.py',
    ],
    test_suite='nose.collector',
)



