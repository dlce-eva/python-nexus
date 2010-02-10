"""Tests for utils in bin directory"""
import os
import re

import nose

from nexus import NexusReader, NexusWriter
from nexus.bin.nexus_treemanip import *


EXAMPLE_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'examples')
        
class Test_TreeManip_run_deltree:
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        run_deltree('1', {}, do_print=False)
        
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        run_deltree('1', "I AM NOT A NEXUS", do_print=False)
    
    def test_run_deltree(self):
        #(options, nexus, do_print=True)
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
        new_nex = run_deltree('2', nexus, do_print=False)
        assert len(new_nex.trees.trees) == 2
        assert new_nex.trees.ntrees == 2
        assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
        assert new_nex.trees[1].startswith('tree tree.20000.883.396049')
    

class Test_TreeManip_run_resample:

    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        run_deltree('1', {}, do_print=False)
        
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        run_deltree('1', "I AM NOT A NEXUS", do_print=False)
        
    def test_run_resample_1(self):
        # shouldn't resample anything..
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example.trees'))
        new_nex = run_resample('1', nexus, do_print=False)
        assert len(new_nex.trees.trees) == 3
        assert new_nex.trees.ntrees == 3
        assert new_nex.trees[0].startswith('tree tree.0.1065.603220')
        assert new_nex.trees[1].startswith('tree tree.10000.874.808756')
        assert new_nex.trees[2].startswith('tree tree.20000.883.396049')


class Test_TreeManip_run_removecomments:
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        run_removecomments({}, do_print=False)
        
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        run_removecomments("I AM NOT A NEXUS", do_print=False)
        
    def test_run_removecomments(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example_beast.trees'))
        new_nex = run_removecomments(nexus, do_print=False)
        assert '[&lnP=-15795.47019648783]' not in new_nex.trees[0]

        
class Test_TreeManip_run_randomise:
    
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_1(self):
        run_random(100, {})
        
    @nose.tools.raises(AssertionError)
    def test_failure_on_nonnexus_2(self):
        run_random(100, "I AM NOT A NEXUS")
    
    @nose.tools.raises(ValueError)
    def test_failure_on_nonint(self):
        run_random('fudge', 
            NexusReader(os.path.join(EXAMPLE_DIR, 'example-translated.trees')))
        
    def test_run_randomise_sample1(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example-translated.trees'))
        new_nex = run_random(1, nexus)
        assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 1
        
    def test_run_randomise_sample2(self):
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example-translated.trees'))
        new_nex = run_random(2, nexus)
        assert new_nex.trees.ntrees == len(new_nex.trees.trees) == 2
    
    @nose.tools.raises(ValueError)
    def test_run_randomise_sample_toobig(self):
        # raises ValueError, sample size too big (only 3 trees in this file)
        nexus = NexusReader(os.path.join(EXAMPLE_DIR, 'example-translated.trees'))
        new_nex = run_random(10, nexus)

