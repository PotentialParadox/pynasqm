'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.trajectories.fluorescencesnaps import FluorescenceSnaps
from pynasqm.inputceon import InputCeon
from pynasqm.utils import mkdir

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/fluorescenceSnapsTests")

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
    user_input.n_steps_exc = 10
    user_input.exc_run_time = 0.005 #ps
    user_input.n_steps_print_emcrd = 1
    user_input.n_steps_to_print_exc = 1
    user_input.time_step = 0.5 #fs
    user_input.n_snapshots_ex = 4
    user_input.n_mcrd_frames_per_run_qmexcited = 10
    user_input.fluorescence_time_delay=0 #fs
    user_input.n_exc_runs = 1
    user_input.restart_attempt = 0
    return user_input

@pytest.fixture
def inputCeon():
    return InputCeon(amber_input='md_qmmm_amb.in', directory='./')


def test_fluTimeDelay(userInput, inputCeon):
    '''
    Only create snapshots after the time delay
    '''
    subprocess.run(['rm', '-rf', 'abs', './convert_to_crd.out', './convert_to_crd.out'])
    userInput.fluorescence_time_delay=1 #fs
    userInput.restart_attempt = 0
    flu_traj = FluorescenceSnaps(userInput, inputCeon)
    flu_traj.create_restarts_from_parent()
    if not os.path.isfile("fluorescence/traj_1/6/snap_6_for_fluorescence_t1.rst"):
        raise AssertionError("FluorescenceSnaps did not create enough snaps")
    if os.path.isfile("fluorescence/traj_1/9/snap_9_for_fluorescence_t1.rst"):
        raise AssertionError("FluorescenceSnaps created too many snaps possibly ignoring time delay")
    subprocess.run(['rm', '-rf', 'fluorescence', './convert_to_crd.out', './convert_to_crd.out'])

def test_fluInputFileCopying(userInput, inputCeon):
    '''
    Create the input files for the intial part of 2 trajectories
    '''
    userInput.restart_attempt = 0
    flu_traj = FluorescenceSnaps(userInput, inputCeon)
    flu_traj.create_inputceon_copies()
    if not os.path.isfile("fluorescence/traj_1/1/nasqm_fluorescence_t1_1.in"):
        raise AssertionError("FluorescenceSnaps did not create nasqm_fluorescence_t1_1.in")
    subprocess.run(['rm', '-rf', 'fluorescence', './convert_to_crd.out', './convert_to_crd.out'])

def test_fluPrepareDynamics(userInput, inputCeon):
    '''
    Prepare dynamics for the snapshots for 1 trajectory
    '''
    userInput.restart_attempt = 0
    userInput.is_hpc = True
    userInput.fluorescence_time_delay=1 #fs
    flu_traj = FluorescenceSnaps(userInput, inputCeon)
    _, slurm_file = flu_traj.prepareScript()
    answer = open("flu_slurm_attempt_test.sbatch").read()
    open("failed_attempt.txt", 'w').write(slurm_file)
    assert slurm_file == answer
    subprocess.run(['rm', 'failed_attempt.txt'])

