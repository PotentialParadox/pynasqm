'''
A unit tester for nasqm_slurm.py
Things were tested on Hypergator 2 at the University of Florida
'''
import os
import pytest
import types
from pynasqm.userinput import UserInput
import pynasqm.nasqmslurm as nasqm_slurm

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/nasqmSlurmTests")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

@pytest.fixture
def userinput():
    '''
    Create a test user input
    '''
    user_input = types.SimpleNamespace()
    user_input.job_name = "test"
    user_input.email = "dtracy.uf@gmail.com"
    user_input.qos = "roitberg"
    user_input.email_options = 2
    user_input.number_nodes = 1
    user_input.processors_per_node = 16
    user_input.memory_per_node = "2000mb"
    user_input.walltime = "00:01:00"
    user_input.max_jobs = 4
    user_input.qmground_traj_index_file = ""
    user_input.n_snapshots_qmground = 0
    return user_input

class Amber:
    '''
    Mock amber class
    '''
    def __init__(self):
        self.input_roots = None
        self.output_roots = None
        self.from_restart = False

@pytest.fixture
def amber():
    '''
    return a mock amber object
    '''
    return Amber()

def test_create_slurm_header(userinput):
    '''
    Test the simple create slurm header function, could
    break if someone messes with the user input class
    '''
    slurm_header = nasqm_slurm.create_slurm_header(userinput)
    comparison = {'n_nodes': 1, 'ppn': 16, 'email_options': 2,
                  'max_jobs': 4, 'email': 'dtracy.uf@gmail.com',
                  'walltime': '00:01:00', 'memory': '2000mb', 'qos': 'roitberg'}
    assert slurm_header == comparison


def test_build_command(amber):
    '''
    Tests the build command
    '''
    amber.input_roots = ["nasqm_abs_${ID}"]
    amber.coordinate_files = ["ground_snap.${ID}"]
    amber.output_roots = ["nasqm_abs_${ID}"]
    amber.restart_files = ["nasqm_abs_${ID}.rst"]
    directory = "${ID}"
    result = nasqm_slurm.build_trajectory_command(directory, amber)
    test = open("nasqm_slurm_build_command.txt", 'r').read()
    assert result == test


def test_slurm_trajectory_file_1(userinput, amber):
    '''
    Tests to see if slurm trajectory_file is capable of running
    one abs trajectory
    '''
    amber.input_roots = ["nasqm_abs_${ID}"]
    amber.coordinate_files = ["ground_snap.${ID}"]
    amber.output_roots = ["nasqm_abs_${ID}"]
    amber.restart_files = ["nasqm_abs_${ID}.rst"]
    title = "MyJob"
    userinput.n_snapshots_qmground = 1
    directory = "${ID}"
    result = nasqm_slurm.slurm_trajectory_files(userinput, amber, title, "qmground", directory)
    test = open("nasqm_slurm_1.txt", 'r').read()
    assert result == test


def test_slurm_trajectory_file_16(userinput, amber):
    '''
    Tests to see if slurm trajectory_file is capable of running
    one whole trajectory
    '''
    amber.input_roots = ["nasqm_abs_${ID}"]
    amber.coordinate_files = ["ground_snap.${ID}"]
    amber.output_roots = ["nasqm_abs_${ID}"]
    amber.restart_files = ["nasqm_abs_${ID}.rst"]
    userinput.n_snapshots_qmground = 16
    title = "MyJob"
    directory = "${ID}"
    result = nasqm_slurm.slurm_trajectory_files(userinput, amber, title, "qmground", directory)
    test = open("nasqm_slurm_16.txt", 'r').read()
    assert result == test

def test_nasqm_restart(userinput):
    restart_attempt = 1
    job_id = 1
    result = nasqm_slurm.nasqm_restart_script(userinput, job_id, restart_attempt)
    test = open("nasqm_restart.sbatch").read()
    assert result == test
