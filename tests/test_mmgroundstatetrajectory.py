'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.mmgroundstatetrajectory import prepareDynamics, create_restarts_from_parent
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
    if os.path.isfile('nasqm_ground.nc'):
        os.chdir("../../..")
    else:
        os.chdir("../..")

def mkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

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
    user_input.n_steps_per_run_gs = 1
    user_input.n_steps_print_gmcrd = 10
    user_input.n_steps_to_print_gs = 15
    user_input.ground_state_time_step = 0.05
    return user_input

def test_prepareDynamcs1of1(userInput):
    '''
    Test for a ground state trajectory using no restarts
    '''
    userInput.restart_attempt = 0
    _, slurm_file = prepareDynamics(userInput)
    result = "\n".join((slurm_file.splitlines())[-10:])
    answer = open("1of1_slurm_attempt_test.sbatch").read()
    assert result == answer
    subprocess.call(['rm', 'nasqm_ground.in', 'failed_test.txt'])

def test_create_restarts(mdQmmmAmb, userInput):
    '''
    Create the original mmground trajectory"
    '''
    userInput.n_ground_runs = 2
    userInput.restart_attempt = 0
    open("m1.prmtop", 'w').close()
    open("input.ceon", 'w').close()
    open("m1.inpcrd", 'w').close()
    create_restarts_from_parent(mdQmmmAmb, userInput)
    if not os.path.isfile("mmground/restart_0/m1.prmtop"):
        raise AssertionError("Did not correctly initiate mmground restart 0 with m1.prmtop")
    if not os.path.isfile("mmground/restart_0/input.ceon"):
        raise AssertionError("Did not correctly initiate mmground restart 0 with input.ceon")
    if not os.path.isfile("mmground/restart_0/nasqm_ground_r0.in"):
        raise AssertionError("Did not correctly initiate mmground restart 0 with nasqm_ground_r0.in")
    amb_input = open("mmground/restart_0/nasqm_ground_r0.in").read()
    if "ntx=1" not in amb_input:
        raise AssertionError("Random velocities were not given in initial mm trajectory")
    if not os.path.isfile("mmground/restart_0/snap_for_mm_r0.rst"):
        raise AssertionError("Did not correctly initiate mmground restart 0 with the restart file snap_for_mm_r0.rst")
    subprocess.call(['rm', '-rf', 'mmground'])


def test_create_restarts1(mdQmmmAmb, userInput):
    '''
    Create the first mmground restart trajectory"
    '''
    userInput.n_ground_runs = 2
    userInput.restart_attempt = 1
    mkdir("mmground")
    mkdir("mmground/restart_0")
    open("mmground/restart_0/m1.prmtop", 'w').close()
    open("mmground/restart_0/input.ceon", 'w').close()
    open("mmground/restart_0/m1.inpcrd", 'w').close()
    open("mmground/restart_0/snap_for_mm_r1.rst", 'w').close()
    create_restarts_from_parent(mdQmmmAmb, userInput)
    if not os.path.isfile("mmground/restart_1/m1.prmtop"):
        raise AssertionError("Did not correctly initiate mmground restart 1 with m1.prmtop")
    if not os.path.isfile("mmground/restart_1/input.ceon"):
        raise AssertionError("Did not correctly initiate mmground restart 1 with input.ceon")
    if not os.path.isfile("mmground/restart_1/nasqm_ground_r1.in"):
        raise AssertionError("Did not correctly initiate mmground restart 1 with nasqm_ground_r1.in")
    amb_input = open("mmground/restart_1/nasqm_ground_r1.in").read()
    if "ntx=5" not in amb_input:
        raise AssertionError("Random velocities were given in a mm restart trajectory")
    if not os.path.isfile("mmground/restart_1/snap_for_mm_r1.rst"):
        raise AssertionError("Did not correctly initiate mmground restart 1 with the restart file snap_for_mm_r1.rst")
    subprocess.call(['rm', '-rf', 'mmground'])
