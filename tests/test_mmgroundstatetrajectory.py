'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.mmgroundstatetrajectory import prepareDynamics
from pynasqm.inputceon import InputCeon

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/mmGroundStatetrajectory")

def teardown_module(module):
    '''
    Return to main directory
    '''
    if os.path.isfile('nasqm_ground_r0.nc'):
        os.chdir("../../..")
    else:
        os.chdir("../..")

@pytest.fixture
def mdQmmmAmb():
    return InputCeon("md_qmmm_amb.in", '.')

@pytest.fixture
def userInput():
    user_input = types.SimpleNamespace()
    user_input.is_qmmm = False
    user_input.is_hpc = True
    user_input.number_nodes = 1
    user_input.processors_per_node = 16
    user_input.memory_per_node = "2000mb"
    user_input.max_jobs = 4
    user_input.job_name = "MyJob"
    user_input.walltime = "00:01:00"
    user_input.qos = "roitberg"
    user_input.email = "dtracy.uf@gmail.com"
    user_input.email_options = 2
    user_input.n_steps_gs = 1
    user_input.n_steps_print_gmcrd = 10
    user_input.n_steps_to_print_gs = 15
    user_input.time_step = 0.05
    return user_input

def test_prepareDynamcs1of1(mdQmmmAmb, userInput):
    '''
    Test for a ground state trajectory using no restarts
    '''
    _, (_, slurm_file) = prepareDynamics(mdQmmmAmb, userInput)
    answer = open("1of1_slurm_attempt_test.sbatch").read()
    assert slurm_file == answer
