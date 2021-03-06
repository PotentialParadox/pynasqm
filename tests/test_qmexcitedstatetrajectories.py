'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.trajectories.qmexcitedstatetrajectories import QmExcitedStateTrajectories
from pynasqm.trajectories.create_restarts import create_restarts_from_parent
from pynasqm.inputceon import InputCeon
from pynasqm.utils import mkdir, touch

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/qmExcitedTrajectories")

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
    user_input.qmexcited_traj_index_file = ""
    user_input.time_step = 0.05
    user_input.ground_state_run_time = 0.01
    user_input.n_snapshots_ex = 2
    user_input.n_mcrd_frames_es = 5
    user_input.n_ground_runs = 2
    user_input.n_flu_runs = 2
    user_input.n_qmground_runs = 2
    user_input.restart_attempt = 0
    user_input.restrain_solvents = True
    return user_input

@pytest.fixture
def inputCeon():
    return InputCeon(amber_input='md_qmmm_amb.in', directory='./')

def test_fluCreateFromQmground(userInput, inputCeon):
    '''
    Create the restart files for the initial trajectory part of two trajectories
    '''
    mkdir("qmground")
    mkdir("qmground/traj_1")
    mkdir("qmground/traj_2")
    mkdir("qmground/traj_1/restart_1")
    mkdir("qmground/traj_2/restart_1")
    mkdir("qmground/traj_1/nmr")
    mkdir("qmground/traj_2/nmr")
    touch("qmground/traj_1/restart_1/snap_for_qmground_t1_r2.rst")
    touch("qmground/traj_2/restart_1/snap_for_qmground_t2_r2.rst")
    open("qmground/traj_1/nmr/rst_1.dist", 'w').write("rst_1")
    open("qmground/traj_2/nmr/rst_2.dist", 'w').write("rst_2")
    open("qmground/traj_1/nmr/closest_1.txt", 'w').write("rst_1")
    open("qmground/traj_2/nmr/closest_2.txt", 'w').write("rst_2")
    flu_traj = QmExcitedStateTrajectories(userInput, inputCeon)
    override = False
    create_restarts_from_parent(flu_traj.traj_data, 0, override=True)
    if not os.path.isfile("qmexcited/traj_1/restart_0/snap_for_qmexcited_t1_r0.rst"):
        raise AssertionError("QmExcitedStateTrajectory did not create snap_for_qmexcited_t1_r0.rst")
    if not os.path.isfile("qmexcited/traj_2/restart_0/snap_for_qmexcited_t2_r0.rst"):
        raise AssertionError("QmExcitedStateTrajectory did not create snap_for_qmexcited_t2_r0.rst")
    if os.path.isdir("ground_snap.3"):
        raise AssertionError("QmExcitedStateTrajectory created too many ground_snaps")
    if os.path.isdir('"qmexcited/traj_3'):
        raise AssertionError("QmExcitedStateTrajectory created too many directories")
    if open("qmexcited/traj_1/nmr/rst_1.dist").read() != "rst_1":
        raise AssertionError("QmExcitedStateTrajectory did not copy nmr data from qmground for traj 1")
    if open("qmexcited/traj_2/nmr/rst_2.dist").read() != "rst_2":
        raise AssertionError("QmExcitedStateTrajectory did not copy nmr data from qmground for traj 2")
    subprocess.run(['rm', '-rf', 'qmexcited', './convert_to_crd.out', './convert_to_crd.out', 'qmground'])


def test_fluCreateFromQmGroundFail(userInput, inputCeon):
    '''
    Make sure the program doesn't crash if the qmground restart file wasn't created
    In this instance the first trajectory didn't produce an appropriate output
    '''
    mkdir("qmground")
    mkdir("qmground/traj_1")
    mkdir("qmground/traj_2")
    mkdir("qmground/traj_1/restart_1")
    mkdir("qmground/traj_2/restart_1")
    mkdir("qmground/traj_1/nmr")
    mkdir("qmground/traj_2/nmr")
    open("qmground/traj_1/nmr/rst_1.dist", 'w').write("rst_1")
    open("qmground/traj_2/nmr/rst_2.dist", 'w').write("rst_2")
    open("qmground/traj_1/nmr/closest_1.txt", 'w').write("rst_1")
    open("qmground/traj_2/nmr/closest_2.txt", 'w').write("rst_2")
    # Failed touch("qmground/traj_2/restart_1/snap_for_qmground_t1_r2.rst")
    touch("qmground/traj_2/restart_1/snap_for_qmground_t2_r2.rst")
    flu_traj = QmExcitedStateTrajectories(userInput, inputCeon)
    create_restarts_from_parent(flu_traj.traj_data, 0, override=True)
    # if not os.path.isfile("qmexcited/traj_1/restart_0/snap_for_qmexcited_t1_r0.rst"):
    #     raise AssertionError("QmExcitedStateTrajectory did not create a snap_for_qmexcited_t1_r0.rst Dummy")
    if not os.path.isfile("qmexcited/traj_2/restart_0/snap_for_qmexcited_t2_r0.rst"):
        raise AssertionError("QmExcitedStateTrajectory did not create snap_for_qmexcited_t2_r0.rst")
    subprocess.run(['rm', '-rf', 'qmexcited', './convert_to_crd.out', './convert_to_crd.out', 'qmground'])

def test_fluCreateFromRestarts(userInput, inputCeon):
    '''
    Create the restart files for the second set of flu trajectories
    '''
    mkdir("flu")
    mkdir("qmexcited/traj_1")
    mkdir("qmexcited/traj_2")
    mkdir("qmexcited/traj_1/restart_0")
    mkdir("qmexcited/traj_2/restart_0")
    mkdir("qmexcited/traj_1/nmr")
    mkdir("qmexcited/traj_2/nmr")
    touch("qmexcited/traj_1/restart_0/snap_for_qmexcited_t1_r1.rst")
    touch("qmexcited/traj_2/restart_0/snap_for_qmexcited_t2_r1.rst")
    open("qmexcited/traj_1/nmr/rst_1.dist", 'w').write("rst_1")
    open("qmexcited/traj_2/nmr/rst_2.dist", 'w').write("rst_2")
    open("qmexcited/traj_1/nmr/closest_1.txt", 'w').write("rst_1")
    open("qmexcited/traj_2/nmr/closest_2.txt", 'w').write("rst_2")
    userInput.restart_attempt = 1
    flu_traj = QmExcitedStateTrajectories(userInput, inputCeon)
    override = False
    create_restarts_from_parent(flu_traj.traj_data, 0, override=True)
    if not os.path.isfile("qmexcited/traj_1/restart_1/snap_for_qmexcited_t1_r1.rst"):
        raise AssertionError("QmExcitedStateTrajectory did not create snap_for_qmexcited_t1_r1.rst")
    if not os.path.isfile("qmexcited/traj_2/restart_1/snap_for_qmexcited_t2_r1.rst"):
        raise AssertionError("QmExcitedStateTrajectory did not create snap_for_qmexcited_t2_r1.rst")
    if "rst_1" not in open("qmexcited/traj_1/nmr/rst_1.dist").read():
        raise AssertionError("QmExcitedStateTrajectory updated nmr of traj_1 during the first restart")
    if "rst_2" not in open("qmexcited/traj_2/nmr/rst_2.dist").read():
        raise AssertionError("QmExcitedStateTrajectory updated nmr of traj_2 during the first restart")
    if "rst_1" not in open("qmexcited/traj_1/nmr/closest_1.txt").read():
        raise AssertionError("QmExcitedStateTrajectory updated nmr of traj_1 during the first restart")
    if "rst_2" not in open("qmexcited/traj_2/nmr/closest_2.txt").read():
        raise AssertionError("QmExcitedStateTrajectory updated nmr of traj_2 during the first restart")
    subprocess.run(['rm', '-rf', 'qmexcited', './convert_to_crd.out', './convert_to_crd.out', 'qmground'])


def test_fluPrepareDynamics0(userInput, inputCeon):
    '''
    Prepare dynamics for the zeroth restart of two trajectories
    '''
    userInput.restart_attempt = 0
    fluTraj = QmExcitedStateTrajectories(userInput, inputCeon)
    _, slurm_file = fluTraj.prepareScript()
    result = "\n".join((slurm_file.splitlines())[-10:])
    answer = open("1of2_slurm_attempt_test.sbatch").read()
    assert result == answer


def test_fluPrepareDynamics1(userInput, inputCeon):
    '''
    Prepare dynamics for the first restart of two trajectories
    '''
    userInput.restart_attempt = 1
    fluTraj = QmExcitedStateTrajectories(userInput, inputCeon)
    _, slurm_file = fluTraj.prepareScript()
    result = "\n".join((slurm_file.splitlines())[-10:])
    answer = open("2of2_slurm_attempt_test.sbatch").read()
    assert result == answer
