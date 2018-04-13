'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.findshift import ev_energy, nm_energy, find_shift
from pynasqm.findshift import find_row_of_max

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


# Maxis 2.910 426.0624999253
def test_findrowmax():
    matrix = np.array([[1, 2, 1.5],[3, 4, 1.8],[5, 6, 1.6]])
    test_index = find_row_of_max(matrix)
    assert test_index == 1

def test_nm_energy():
    matrix = np.array([[1, 2, 1.5],[3, 4, 1.8],[5, 6, 1.6]])
    row_max = 1
    test_energy = nm_energy(matrix, row_max)
    assert test_energy == 4

def test_nm_energy():
    matrix = np.array([[1, 2, 1.5],[3, 4, 1.8],[5, 6, 1.6]])
    row_max = 1
    test_energy = ev_energy(matrix, row_max)
    assert test_energy == 3

def test_findshift_ev():
    file1 = "findshift_test1.out"
    file2 = "findshift_test2.out"
    units = "ev"
    shift = find_shift(file1, file2, units)
    answer = 0.06
    np.testing.assert_almost_equal(shift, answer)

