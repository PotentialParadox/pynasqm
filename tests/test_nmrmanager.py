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
    restricted_atoms = types.SimpleNamespace()
    restricted_atoms.solvent_atoms = [[2041]]
    restricted_atoms.solute_atoms = [[1]]
    atom_array = [restricted_atoms]
    writer = NMRManager(input_ceons, closest_outputs, atom_array)
    result_file = "rst_1.dist"
    writer.write_dist_files()
    result = open(result_file, 'r').read()
    answer_file = "nmr_manager_test.dist"
    answer = open(answer_file, 'r').read()
    assert result == answer

def test_update_inputs():
    amber_input_name = "md_qmmm_amb.in"
    original_input_ceons = InputCeon(amber_input_name)
    test_name = "nmr_manager.in"
    new_input_ceon = original_input_ceons.copy(test_name)
    input_ceons = [new_input_ceon]
    restricted_atoms = types.SimpleNamespace()
    restricted_atoms.solvent_atoms = [[2041]]
    restricted_atoms.solute_atoms = [[1]]
    atom_array = [restricted_atoms]
    closest_outputs = ["closest_1.txt"]
    dist_file_input = ['./rst_1.dist']
    manager = NMRManager(input_ceons, closest_outputs, atom_array, dist_files=dist_file_input)
    manager.update_inputs()
    answer = open("nmr_manager_test.in", 'r').read()
    result = open(test_name, 'r').read()
    assert result == answer
