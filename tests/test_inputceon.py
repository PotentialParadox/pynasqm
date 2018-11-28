'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
from pynasqm.inputceon import InputCeon

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/inputceon")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

def test_set_nmr_directory():
    amber_input_name = "md_qmmm_amb.in"
    original_input_ceons = InputCeon(amber_input_name, ".")
    test_name = "nmr_directory.in"
    new_input_ceon = original_input_ceons.copy("1/", test_name)
    nmr_directory = "./rest_1.dist"
    new_input_ceon.set_nmr_directory(nmr_directory)
    answer_file = "test_nmr_directory.in"
    answer = open(answer_file, 'r').read()
    result = open("1/" + test_name, 'r').read()
    assert answer == result
