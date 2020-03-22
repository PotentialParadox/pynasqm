'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import subprocess
import types
import pytest
from pynasqm.trajectories.absorptionsnaps import AbsorptionSnaps
from pynasqm.inputceon import InputCeon
from pynasqm.utils import mkdir

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/absorptionSnapsTests")

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
    user_input.n_steps_qmground = 20
    user_input.qmground_run_time = 0.01 #ps
    user_input.n_steps_print_qmgmcrd = 2
    user_input.n_steps_to_print_qmground = 1
    user_input.time_step = 0.5 #fs
    user_input.n_snapshots_qmground = 4
    user_input.n_mcrd_frames_per_run_qmground = 5
    user_input.absorption_time_delay=5 #fs
    user_input.n_qmground_runs = 2
    user_input.restart_attempt = 0
    return user_input

@pytest.fixture
def inputCeon():
    return InputCeon(amber_input='md_qmmm_amb.in', directory='./')


# def test_absCreateRestarts(userInput, inputCeon):
#     '''
#     Create the restart files for the initial trajectory part of two trajectories
#     '''
#     subprocess.run(['rm', '-rf', 'abs', './convert_to_crd.out', './convert_to_crd.out'])
#     userInput.absorption_time_delay=0 #fs
#     abs_traj = AbsorptionSnaps(userInput, inputCeon)
#     abs_traj.create_restarts_from_parent()
#     if not os.path.isfile("abs/traj_1/1/snap_1_for_absorption_t1.rst"):
#         raise AssertionError("AbsorptionSnaps did not create snap_1_for_absorption_t1.rst")
#     if not os.path.isfile("abs/traj_2/1/snap_1_for_absorption_t2.rst"):
#         raise AssertionError("AbsorptionSnaps did not create snap_2_for_absorption_t2.rst")
#     subprocess.run(['rm', '-rf', 'abs', './convert_to_crd.out', './convert_to_crd.out'])

def test_absTimeDelay(userInput, inputCeon):
    '''
    Only create snapshots after the time delay
    '''
    subprocess.run(['rm', '-rf', 'abs', './convert_to_crd.out', './convert_to_crd.out'])
    userInput.absorption_time_delay=5 #fs
    userInput.restart_attempt = 0
    abs_traj = AbsorptionSnaps(userInput, inputCeon)
    abs_traj.create_restarts_from_parent()
    if os.path.isfile("absorption/traj_1/6/snap_6_for_absorption_t1.rst"):
        raise AssertionError("AbsorptionSnaps created too many snaps possibly ignoring time delay")
    subprocess.run(['rm', '-rf', 'absorption', './convert_to_crd.out', './convert_to_crd.out'])

def test_absInputFileCopying(userInput, inputCeon):
    '''
    Create the input files for the intial part of 2 trajectories
    '''
    userInput.restart_attempt = 0
    abs_traj = AbsorptionSnaps(userInput, inputCeon)
    abs_traj.create_inputceon_copies()
    if not os.path.isfile("absorption/traj_1/1/nasqm_absorption_t1_1.in"):
        raise AssertionError("AbsorptionSnaps did not create nasqm_absorption_t1_1.in")
    subprocess.run(['rm', '-rf', 'absorption', './convert_to_crd.out', './convert_to_crd.out'])

def test_absPrepareDynamics(userInput, inputCeon):
    '''
    Prepare dynamics for the snapshots for 1 trajectory
    '''
    userInput.restart_attempt = 0
    userInput.is_hpc = True
    userInput.absorption_time_delay=5 #fs
    abs_traj = AbsorptionSnaps(userInput, inputCeon)
    _, slurm_file = abs_traj.prepareScript()
    answer = open("abs_slurm_attempt_test.sbatch").read()
    open("failed_attempt.txt", 'w').write(slurm_file)
    assert slurm_file == answer
    subprocess.run(['rm', 'failed_attempt.txt'])

# def test_qmGroundPrepareDynamics1(userInput, inputCeon):
#     '''
#     Prepare dynamics for the first restart of two trajectories
#     '''
#     userInput.restart_attempt = 1
#     userInput.is_hpc = True
#     qmground_traj = QmGroundTrajectories(userInput, inputCeon)
#     _, slurm_file = qmground_traj.prepareScript()
#     result = "\n".join((slurm_file.splitlines())[-10:])+"\n"
#     answer = open("2of2_slurm_attempt_test.sbatch").read()
#     open("failed1.txt", 'w').write(result)
#     assert result == answer
#     subprocess.run(['rm', 'failed_attempt.txt'])

# def test_restart_on_failed(userInput, inputCeon):
#     '''
#     Make sure the program doesn't crash if the trajectory we are restarting from a failed trajectory.
#     If rst isn't there, make a dummy. I can let amber handle the failure.
#     In the test below the second trajectory is mocked to fail.
#     '''
#     userInput.n_snapshots_gs = 2
#     userInput.n_qmground_runs = 2
#     userInput.restart_attempt = 1
#     if not os.path.exists("qmground"):
#         os.mkdir("qmground")
#         os.mkdir("qmground/traj_1")
#         os.mkdir("qmground/traj_1/restart_0")
#         os.mkdir("qmground/traj_2")
#         os.mkdir("qmground/traj_2/restart_0")
#     open("qmground/traj_1/restart_0/snap_for_abs_t1_r1.rst", 'w').close()
#     # Failure here
#     qmground_traj = QmGroundTrajectories(userInput, inputCeon)
#     qmground_traj.create_restarts_from_parent()
#     # if not os.path.isfile("abs/traj_2/restart_1/snap_for_abs_t2_r1.rst"):
#     #     raise AssertionError("AbsTrajectory did not create a dummy snap_for_abs_t2_r1")
#     if os.path.isdir("qmground/traj_3"):
#         raise AssertionError("QmGroundTrajectories created too many trajectories")
#     if os.path.isdir("qmground/traj_1/restart_2"):
#         raise AssertionError("QmGroundTrajectories created too many restarts")
#     subprocess.run(['rm', '-rf', 'qmground'])

