from setuptools import setup, find_packages


setup(
    name="python-nexus",
    version="2.1.0",
    description="A nexus (phylogenetics) file reader (.nex, .trees)",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="phylogenetics nexus newick paup splitstree",
    author="Simon Greenhill and Robert Forkel",
    author_email="simon@simon.net.nz",
    url="https://github.com/shh-dlce/python-nexus",
    license="BSD-2-Clause",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'nexus=nexus.__main__:main',
        ],
    },
    platforms='any',
    python_requires='>=3.5',
    install_requires=[
        'newick',
        'clldutils>=3.5',
        'termcolor',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=5',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
)
