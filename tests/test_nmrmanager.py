'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import types
import pytest
from pynasqm.nmrmanager import NMRManager
from pynasqm.inputceon import InputCeon

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

def test_write_dist_files():
    input_ceons = ["md_qmmm.in"]
    user_input = types.SimpleNamespace()
    user_input.mask_for_center = "@1"
    user_input.desired_distance = 4
    user_input.number_nearest_solvents = 1
    closest_outputs = ["closest_1.txt"]
    writer = NMRManager(input_ceons, user_input, closest_outputs)
    result_file = "rst_1.dist"
    writer.write_dist_files()
    result = open(result_file, 'r').read()
    answer_file = "nmr_manager_test.dist"
    answer = open(answer_file, 'r').read()
    assert result == answer

def test_residue_mask_error():
    input_ceons = ["md_qmmm.in"]
    user_input = types.SimpleNamespace()
    user_input.mask_for_center = ":1"
    user_input.desired_distance = 4
    closest_outputs = ["closest_1.txt"]
    manager = NMRManager(input_ceons, user_input, closest_outputs)
    with pytest.raises(Exception):
        manager.write_dist_files()

def test_update_inputs():
    amber_input_name = "md_qmmm_amb.in"
    original_input_ceons = InputCeon(amber_input_name)
    test_name = "mask_updater.in"
    new_input_ceon = original_input_ceons.copy(test_name)
    input_ceons = [new_input_ceon]
    user_input = types.SimpleNamespace()
    user_input.mask_for_center = "@1"
    user_input.desired_distance = 4
    closest_outputs = ["closest_1.txt"]
    dist_file_input = ['rst_1.dist']
    manager = NMRManager(input_ceons, user_input, closest_outputs, dist_files=dist_file_input)
    manager.update_inputs()
