'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.fluorescencetrajectories import FluTrajectories
from pynasqm.inputceon import InputCeon

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/fluorescenceTrajectories")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

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
    user_input.ground_state_run_time = 0.01
    user_input.n_snapshots_ex = 2
    user_input.n_mcrd_frames_es = 5
    user_input.n_ground_runs = 2
    user_input.n_abs_runs = 2
    user_input.restart_attempt = 0
    return user_input

@pytest.fixture
def inputCeon():
    return InputCeon(amber_input='md_qmmm_amb.in', directory='./')

def test_createInputceonCopies0(userInput, inputCeon):
    '''
    Create the input files needed for the zeroth restart of two trajectories at restart 0
    '''
    userInput.restart_attempt = 0
    fluTraj = FluTrajectories(userInput, inputCeon)
    fluTraj.create_inputceon_copies()
    if not os.path.isfile('1/nasqm_flu_1.in'):
        print(subprocess.call(['ls', '1']))
        raise AssertionError("FluTrajectory did not create 1/nasqm_abs_1.in")
    if not os.path.isfile('2/nasqm_flu_2.in'):
        print(subprocess.call(['ls', '2']))
        raise AssertionError("FluTrajectory did not create 2/nasqm_abs_2.in")
    subprocess.call(['rm', '1/nasqm_flu_1.in', '2/nasqm_flu_2.in'])

def test_createInputceonCopies1(userInput, inputCeon):
    '''
    Create the input files needed for the zeroth restart of two trajectories at restart 1
    '''
    userInput.restart_attempt = 1
    fluTraj = FluTrajectories(userInput, inputCeon)
    fluTraj.create_inputceon_copies()
    if not os.path.isfile('1/nasqm_flu_1.in'):
        print(subprocess.call(['ls', '1']))
        raise AssertionError("FluTrajectory did not create 1/nasqm_abs_1.in")
    if not os.path.isfile('2/nasqm_flu_2.in'):
        print(subprocess.call(['ls', '2']))
        raise AssertionError("FluTrajectory did not create 2/nasqm_abs_2.in")
    subprocess.call(['rm', '1/nasqm_flu_1.in', '2/nasqm_flu_2.in'])

# def test_fluPrepareDynamics0(userInput, inputCeon):
#     '''
#     Prepare dynamics for the zeroth restart of two trajectories
#     '''
#     userInput.restart_attempt = 0
#     fluTraj = FluTrajectories(userInput, inputCeon)
#     _, (_, slurm_file) = fluTraj.prepareDynamics()
#     answer = open("1of2_slurm_attempt_test.sbatch").read()
#     assert slurm_file == answer

