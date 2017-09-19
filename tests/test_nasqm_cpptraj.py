'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
import pynasqm.cpptraj as nasqm_cpptraj
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
def userinput():
    '''
    Create a test user input
    '''
    user_input = nasqm_user_input.UserInput()
    return user_input

@pytest.fixture
def input_ceon():
    '''
    Create an input_ceon object
    '''
    return inputceon.InputCeon('md_qmmm_amb.in')

def test_closest_script_3(userinput):
    '''
    Test to see if program is capable of building a script
    to include the nearest three solvent molecules
    '''
    userinput.number_nearest_solvents = 3
    snap_id = 1
    result = nasqm_cpptraj.closest_script(userinput, snap_id)
    test = open('nasqm_cpptraj_nearest_three.txt', 'r').read()
    assert result == test

def test_closest_script_4():
    '''
    Test to see if program is capable of building a script
    to include the nearest four solvent molecules
    '''
    userinput.number_nearest_solvents = 4
    snap_id = 1
    result = nasqm_cpptraj.closest_script(userinput, snap_id)
    test = open('nasqm_cpptraj_nearest_four.txt', 'r').read()
    assert result == test

def test_closest_script_5_snap_2():
    '''
    Test to see if it can build a script to include
    the nearest 5 but from the 2nd ground snapshot
    '''
    userinput.number_nearest_solvents = 5
    snap_id = 2
    result = nasqm_cpptraj.closest_script(userinput, snap_id)
    test = open('nasqm_cpptraj_nearest_five.txt', 'r').read()
    assert result == test

def test_read_closest_3():
    '''
    Test to determine if the read closest can read
    the output from the closest three script
    '''
    closest_steam = open('nasqm_cpptraj_closest_1.txt', 'r')
    result = nasqm_cpptraj.read_closest(closest_steam)
    np.testing.assert_array_equal(result, np.array([400, 456, 152]))

def test_read_closest_4():
    '''
    Test to determine if the read closest can read
    the output from the closest 4 script
    '''
    closest_steam = open('nasqm_cpptraj_closest_4.txt', 'r')
    result = nasqm_cpptraj.read_closest(closest_steam)
    np.testing.assert_array_equal(result, np.array([420, 560, 252, 397]))

def test_update_closest_1(input_ceon, userinput):
    '''
    Integration
    Test to see if capable of updating one inputceon
    '''
    userinput.number_nearest_solvents = 3
    test = [input_ceon.copy('test_inputceon.in')]
    nasqm_cpptraj.update_closest(userinput, test)
    result = test[0].get_mask()
    assert result == "':1,400,456,152'"

def test_update_closest_4(input_ceon, userinput):
    '''
    Integration
    Test to see if capable of update one inputceon
    file but with 4 values
    '''
    userinput.number_nearest_solvents = 4
    test = [input_ceon.copy('test_inputceon.in')]
    nasqm_cpptraj.update_closest(userinput, test)
    result = test[0].get_mask()
    assert result == "':1,400,456,152,597'"

def test_update_closest_multi(input_ceon, userinput):
    '''
    Integration
    Test to see if capable of update two inputceon
    files with 3 closest values
    '''
    userinput.number_nearest_solvents = 3
    test = [input_ceon.copy('test_inputceon.in') for _ in range(2)]
    nasqm_cpptraj.update_closest(userinput, test)
    result = test[1].get_mask()
    assert result == "':1,181,668,395'"

def test_update_closest_none(input_ceon, userinput):
    '''
    Integration
    Test to make sure program doesn't fail when
    userinput.number_nearest_solvent = None
    '''
    userinput.number_nearest_solvents = 0
    test = [input_ceon.copy('test_inputceon.in')]
    nasqm_cpptraj.update_closest(userinput, test)
    result = test[0].get_mask()
    assert result == "':1'"
