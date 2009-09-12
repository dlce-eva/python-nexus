from setuptools import setup, find_packages
version = "0.5"

setup(
    name="python-nexus", 
    version=version,
    description="A generic nexus (phylogenetics) file format (.nex, .trees) reader for python",
    classifiers=[
        "Programming Language :: Python", 
        ("Intended Audience :: Science/Research", 
         "License :: OSI Approved :: BSD License",
         "Topic :: Scientific/Engineering",
         "Topic :: Scientific/Engineering :: Bio-Informatics",
         "Topic :: Software Development :: Libraries :: Python Modules",
         ),
    ],
    keywords="phylogenetics nexus newick paup splitstree",
    author="Simon Greenhill",
    author_email="simon@simon.net.nz",
    url="http://simon.net.nz/python-nexus",
    license="BSD",
    packages=find_packages(),
    namespace_packages=['nexus'],
    test_suite='nose.collector',
)

