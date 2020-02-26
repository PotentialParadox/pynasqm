'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.slurm_array_generator import should_read_from_file

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/slurmArrayGenerator")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

@pytest.fixture
def userInput():
    user_input = types.SimpleNamespace()
    user_input.qmground_traj_index_file = "qmgrounds.txt"
    user_input.qmexcited_traj_index_file = "qmexciteds.txt"
    return user_input

def test_should_read_from_file(userInput):
    result = should_read_from_file(userInput, "qmground")
    assert result == True

def test_should_read_from_file_exit(userInput):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        should_read_from_file(userInput, "qmexcited")
    assert pytest_wrapped_e.type == SystemExit
