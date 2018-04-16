'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.nmrgroupgroup import NMRGroupGroup
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

def test_nmrgroupgroup_writer1():
    restricted_atoms1 = [[4055, 4056]]
    restricted_atoms2 = [[4065, 4066]]
    desired_distance = 4
    writer = NMRGroupGroup(restricted_atoms1, restricted_atoms2, desired_distance)
    result_file = "nmr_groupgroup1.dist"
    answer_file = "nmr_groupgroup_test1.dist"
    writer.write_to(result_file)
    result = open(result_file, 'r').read()
    answer = open(answer_file, 'r').read()
    assert result == answer

def test_nmrgrougroup_writer2():
    restricted_atoms1 = [[4055, 4056], [4055, 4056]]
    restricted_atoms2 = [[4065, 4066], [5678, 5679]]
    desired_distance = 4
    writer = NMRGroupGroup(restricted_atoms1, restricted_atoms2, desired_distance)
    result_file = "nmr_groupgroup2dist"
    answer_file = "nmr_groupgroup_test2.dist"
    writer.write_to(result_file)
    result = open(result_file, 'r').read()
    answer = open(answer_file, 'r').read()
    assert result == answer
