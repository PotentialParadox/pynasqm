'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.nmrsinglesingle import NMRSingleSingle
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

def test_nmr_writer1():
    restricted_atoms1 = [[4055]]
    restricted_atoms2 = [[4065]]
    desired_distance = [4]
    writer = NMRSingleSingle(restricted_atoms1, restricted_atoms2, desired_distance)
    result_file = "nmr_singlesingle1.dist"
    answer_file = "nmr_singlesingle_test1.dist"
    writer.write_to(result_file)
    result = open(result_file, 'r').read()
    answer = open(answer_file, 'r').read()
    assert result == answer

def test_nmr_writer2():
    '''
    When we have 2 atoms with want to restrict
    '''
    restricted_atoms1 = [[4055],[4055]]
    restricted_atoms2 = [[4065],[4066]]
    desired_distance = [4,5]
    writer = NMRSingleSingle(restricted_atoms1, restricted_atoms2, desired_distance)
    result_file = "nmr_singlesingle2.dist"
    answer_file = "nmr_singlesingle_test2.dist"
    writer.write_to(result_file)
    result = open(result_file, 'r').read()
    answer = open(answer_file, 'r').read()
    assert result == answer
