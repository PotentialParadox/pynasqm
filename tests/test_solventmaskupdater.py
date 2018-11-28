'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import types
import pytest
from pynasqm.solventmaskupdater import SolventMaskUpdater
from pynasqm.inputceon import InputCeon

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/solventMaskUpdater")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")


def test_mask_updater():
    user_input = types.SimpleNamespace()
    user_input.number_nearest_solvents = 3
    amber_input_name = "md_qmmm_amb.in"
    original_input_ceons = InputCeon(amber_input_name, directory='./')
    test_name = "mask_updater.in"
    new_input_ceon = original_input_ceons.copy('./', test_name)
    input_ceons = [new_input_ceon]
    outputs = ['closest_1.txt']
    updater = SolventMaskUpdater(input_ceons, user_input, outputs)
    updater.update_masks()
    result = open(test_name, 'r').read()
    answer_file = "mask_updater_test.in"
    answer = open(answer_file, 'r').read()
    assert result == answer



