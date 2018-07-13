'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.inputceonwriter import InputceonWriter
from pynasqm.inputceonmanager import InputceonManager

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

def test_generate_initial_coeffs():
    state = 2
    states_to_prop = 3
    result = InputceonManager.generate_initial_coeffs(state, states_to_prop)
    np.testing.assert_array_equal(result, np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 0.0]]))

# def test_set_excited_state():
#     state = 2
#     state_to_prop = 3
#     inputfile = "inputceonmanager_test.ceon"
#     header = "inputceonmanager test\n"
#     manager = InputceonManager(inputfile)
#     outputfile = "inputceonmanager_result.ceon"
#     writer = InputceonWriter(inputfile)
#     writer.write(outputfile)
#     result = open(outputfile, 'r').read()
#     answer = open(inputfile, 'r').read()
#     asser result == answer

