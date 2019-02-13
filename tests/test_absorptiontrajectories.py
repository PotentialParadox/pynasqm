'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.absorptiontrajectories import AbsTrajectories
from pynasqm.inputceon import InputCeon
from pynasqm.utils import mkdir

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/absorptionTrajectories")

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
    user_input.n_snapshots_gs = 2
    user_input.n_mcrd_frames_gs = 5
    user_input.n_ground_runs = 2
    user_input.restart_attempt = 0
    user_input.number_nearest_solvents = 1
    user_input.mask_for_center = ":1"
    user_input.restrain_solvents = True
    return user_input

@pytest.fixture
def inputCeon():
    return InputCeon(amber_input='md_qmmm_amb.in', directory='./')

def test_absCreateRestarts(userInput, inputCeon):
    '''
    Create the restart files for the initial trajectory part of two trajectories
    '''
    userInput.restart_attempt = 0
    abs_traj = AbsTrajectories(userInput, inputCeon)
    abs_traj.create_restarts_from_parent()
    if not os.path.isfile("abs/traj_1/restart_0/snap_for_abs_t1_r0.rst"):
        raise AssertionError("AbsTrajectory did not create snap_for_abs_t1_r0.rst")
    if not os.path.isfile("abs/traj_2/restart_0/snap_for_abs_t2_r0.rst"):
        raise AssertionError("AbsTrajectory did not create snap_for_abs_t2_r0.rst")
    if os.path.isdir("ground_snap.3"):
        raise AssertionError("AbsTrajectory created too many ground_snaps")
    if os.path.isdir('"abs/traj_3'):
        raise AssertionError("AbsTrajectory created too many directories")
    if os.path.isdir('"abs/traj_1/nmr'):
        raise AssertionError("AbsTrajectory did not create the nmr directory for traj_1")
    if os.path.isdir('"abs/traj_2/nmr'):
        raise AssertionError("AbsTrajectory did not create the nmr directory for traj_2")
    subprocess.run(['rm', '-rf', 'abs', './convert_to_crd.out', './convert_to_crd.out'])

def test_absInputFileCopying(userInput, inputCeon):
    '''
    Create the input files for the intial part of 2 trajectories
    '''
    userInput.restart_attempt = 0
    abs_traj = AbsTrajectories(userInput, inputCeon)
    abs_traj.create_inputceon_copies()
    if not os.path.isfile("abs/traj_1/restart_0/nasqm_abs_t1_r0.in"):
        raise AssertionError("AbsTrajectory did not create nasqm_abs_t1_r0.in")


def test_absCreateRestarts1(userInput, inputCeon):
    '''
    Create the input files for the first restart of one trajectories
    '''
    userInput.n_snapshots_gs = 1
    userInput.n_abs_runs = 2
    userInput.restart_attempt = 1
    if not os.path.exists("abs"):
        os.mkdir("abs")
        os.mkdir("abs/traj_1")
        os.mkdir("abs/traj_1/restart_0")
    open("abs/traj_1/restart_0/snap_for_abs_t1_r1.rst", 'w').close()
    abs_traj = AbsTrajectories(userInput, inputCeon)
    abs_traj.create_restarts_from_parent()
    if not os.path.isfile("abs/traj_1/restart_1/snap_for_abs_t1_r1.rst"):
        raise AssertionError("AbsTrajectory did not create snap_for_abs_t1_r1")
    if os.path.isfile("abs/traj_2/restart_2/snap_for_abs_t2_r2.rst"):
        raise AssertionError("AbsTrajectory created too many snaps")
    subprocess.run(['rm', '-rf', 'traj_1', './convert_to_crd.out', './convert_to_crd.out'])


def test_absCreateRestarts1(userInput, inputCeon):
    '''
    Create the input files for the first restart of one trajectories
    '''
    userInput.n_snapshots_gs = 2
    userInput.n_abs_runs = 2
    userInput.restart_attempt = 1
    if not os.path.exists("abs"):
        os.mkdir("abs")
        os.mkdir("abs/traj_1")
        os.mkdir("abs/traj_1/restart_0")
        os.mkdir("abs/traj_2")
        os.mkdir("abs/traj_2/restart_0")
    open("abs/traj_1/restart_0/snap_for_abs_t1_r1.rst", 'w').close()
    open("abs/traj_2/restart_0/snap_for_abs_t2_r1.rst", 'w').close()
    abs_traj = AbsTrajectories(userInput, inputCeon)
    abs_traj.create_restarts_from_parent()
    if not os.path.isfile("abs/traj_1/restart_1/snap_for_abs_t1_r1.rst"):
        raise AssertionError("AbsTrajectory did not create snap_for_abs_t1_r1")
    if not os.path.isfile("abs/traj_2/restart_1/snap_for_abs_t2_r1.rst"):
        raise AssertionError("AbsTrajectory did not create snap_for_abs_t2_r1")
    if os.path.isdir("abs/traj_3"):
        raise AssertionError("AbsTrajectory created too many trajectories")
    if os.path.isdir("abs/traj_1/restart_2"):
        raise AssertionError("AbsTrajectory created too many restarts")
    subprocess.run(['rm', '-rf', 'abs'])


def test_absPrepareDynamics0(userInput, inputCeon):
    '''
    Prepare dynamics for the zeroth restart of two trajectories
    '''
    userInput.restart_attempt = 0
    abs_traj = AbsTrajectories(userInput, inputCeon)
    _, (_, slurm_file) = abs_traj.prepareDynamics()
    answer = open("1of2_slurm_attempt_test.sbatch").read()
    open('failed_attempt.txt', 'w').write(slurm_file)
    assert slurm_file == answer
    subprocess.run(['rm', 'failed_attempt.txt'])

def test_absPrepareDynamics0(userInput, inputCeon):
    '''
    Prepare dynamics for the first restart of two trajectories
    '''
    userInput.restart_attempt = 1
    abs_traj = AbsTrajectories(userInput, inputCeon)
    _, (_, slurm_file) = abs_traj.prepareDynamics()
    answer = open("2of2_slurm_attempt_test.sbatch").read()
    open('failed_attempt.txt', 'w').write(slurm_file)
    assert slurm_file == answer
    subprocess.run(['rm', 'failed_attempt.txt'])

def test_restart_on_failed(userInput, inputCeon):
    '''
    Make sure the program doesn't crash if the trajectory we are restarting from a failed trajectory.
    If rst isn't there, make a dummy. I can let amber handle the failure.
    In the test below the second trajectory is mocked to fail.
    '''
    userInput.n_snapshots_gs = 2
    userInput.n_abs_runs = 2
    userInput.restart_attempt = 1
    if not os.path.exists("abs"):
        os.mkdir("abs")
        os.mkdir("abs/traj_1")
        os.mkdir("abs/traj_1/restart_0")
        os.mkdir("abs/traj_2")
        os.mkdir("abs/traj_2/restart_0")
    open("abs/traj_1/restart_0/snap_for_abs_t1_r1.rst", 'w').close()
    # Failure here
    abs_traj = AbsTrajectories(userInput, inputCeon)
    abs_traj.create_restarts_from_parent()
    if not os.path.isfile("abs/traj_2/restart_1/snap_for_abs_t2_r1.rst"):
        raise AssertionError("AbsTrajectory did not create a dummy snap_for_abs_t2_r1")
    if os.path.isdir("abs/traj_3"):
        raise AssertionError("AbsTrajectory created too many trajectories")
    if os.path.isdir("abs/traj_1/restart_2"):
        raise AssertionError("AbsTrajectory created too many restarts")
    subprocess.run(['rm', '-rf', 'abs'])


def test_nmr_update(userInput, inputCeon):
    '''Assure that the input files of each restart refer to the same nmr data as
    the original trajectory
    '''
    userInput.restart_attempt = 0
    abs_traj = AbsTrajectories(userInput, inputCeon)
    abs_traj.gen_inputfiles()
    amb_input = open("abs/traj_2/restart_0/nasqm_abs_t2_r0.in").read()
    if "DUMPFREQ" not in amb_input:
        raise AssertionError("nasqm_abs_t2_r0.in was not updated for nmr")
    subprocess.call(['rm', 'abs/traj_2/nmr/rst_2.dist'])
    userInput.restart_attempt = 1
    abs_traj = AbsTrajectories(userInput, inputCeon)
    abs_traj.gen_inputfiles()
    amb_input = open("abs/traj_2/restart_1/nasqm_abs_t2_r1.in").read()
    if "DUMPFREQ" not in amb_input:
        raise AssertionError("nasqm_abs_t2_r1.in was not updated for nmr")
    if os.path.isfile("abs/traj_2/nmr/rst_2.dist"):
        raise AssertionError("absorption created new nmr data on restart")

