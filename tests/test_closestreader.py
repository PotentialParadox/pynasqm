'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.closestreader import ClosestReader
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

@pytest.fixture
def closest_output():
    '''
    Create a test user input
    '''
    return open("closest_reader_1.txt", 'r')

def test_atoms(closest_output):
    '''
    Test the reading of atoms from closest_1.txt
    '''
    closests = ClosestReader(closest_output)
    result = closests.atoms
    np.testing.assert_array_equal(result, np.array([2041, 2321, 801]))

def test_residues(closest_output):
    '''
    Test the reading of residues from closest_1.txt
    '''
    closests = ClosestReader(closest_output)
    result = closests.residues
    np.testing.assert_array_equal(result, np.array([400, 456, 152]))

def test_distances(closest_output):
    '''
    Test the reading of residues from closest_1.txt
    '''
    closests = ClosestReader(closest_output)
    result = closests.distances
    print(result)
    np.testing.assert_almost_equal(result, np.array([2.4660, 2.6087, 2.6091]))
