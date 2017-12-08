'''
A unit tester for calculatespectra
'''
import pytest
import os
import numpy as np
from pynasqm.calculatespectra import average_spectra, np_to_string

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

def test_average_spectras():
    '''
    average the two abs spectras that are included in the test suite
    that have 2 states
    '''
    spectra_type = 0 # abs
    number_trajectories = 2
    results = average_spectra(spectra_type, number_trajectories)
    answer = np.array([[2.79, 444.3877687393, 0.00679938765, 0.00110222205, 0.00679938765],
                       [2.81, 441.2248665707, 0.01893529445, 0.0006000568, 0.01893529445],
                       [2.83, 438.1066695345, 0.0490790883, 0.0002592882, 0.0490790883]])
    np.testing.assert_allclose(results, answer, rtol=1e-5)

def test_np_to_string():
    '''
    Test the formatting of np_to_string to make sure it matches the original
    '''
    data = np.array([[2.790, 444.3877687393, 0.0000000242, 0.0000133411, 0.0000000242],
                     [2.810, 441.2248664707, 0.0000091352, 0.0000454145, 0.0000091352],
                     [2.830, 438.1066695345, 0.0002506695, 0.0001086144, 0.0002506695]])
    result = np_to_string(data)
    answer = open("spectra_abs_0.output", 'r').read()
    assert result == answer
