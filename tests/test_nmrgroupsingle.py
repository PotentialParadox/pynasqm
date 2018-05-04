'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.nmrgroupsingle import NMRGroupSingle
import pynasqm.userinput as nasqm_user_input
import pynasqm.inputceon as inputceon

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("..")

def test_nmr_writer():
    restricted_atoms1 = [[4055, 4056]]
    restricted_atoms2 = [[4065]]
    desired_distance = [4]
    writer = NMRGroupSingle(restricted_atoms1, restricted_atoms2, desired_distance)
    result_file = "nmr_groupsingle.dist"
    answer_file = "nmr_groupsingle_test.dist"
    writer.write_to(result_file)
    result = open(result_file, 'r').read()
    answer = open(answer_file, 'r').read()
    assert result == answer
