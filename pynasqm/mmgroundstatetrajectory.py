import functools
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm
import pytraj as pt
from pynasqm.utils import copy_files, mkdir, copy_file
import subprocess

def israndomvelocity(restart_attempt):
    if restart_attempt == 0:
        return True
    return False

def setInput(md_qmmm_amb, user_input):
    restart = user_input.restart_attempt
    destination_file = "mmground/restart_{}/nasqm_ground_r{}.in".format(restart, restart)
    input_ceon = md_qmmm_amb.copy("./", destination_file, True)
    input_ceon.set_n_steps(user_input.n_steps_gs)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_gmcrd)
    input_ceon.set_quantum(False)
    input_ceon.set_exc_state_propagate(0)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_gs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(0)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(israndomvelocity(restart))

def createAmber(user_input):
    restart = user_input.restart_attempt
    amber = Amber()
    amber.input_roots = ["nasqm_ground_r{}".format(restart)]
    amber.output_roots = ["nasqm_ground_r{}".format(restart)]
    amber.prmtop_files = ["m1.prmtop"]
    amber.restart_files = ["snap_for_mm_r{}.rst".format(restart+1)]
    amber.export_roots = ["nasqm_ground_r{}".format(restart)]
    amber.coordinate_files = ["snap_for_mm_r{}.rst".format(restart)]
    amber.directories = ["mmground/restart_{}".format(restart)]
    return amber

def runDynamics(user_input, amber, slurm_files):
    if user_input.is_hpc:
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
    else:
        amber.run_amber(number_processors=1, is_ground_state=True)

def prepareDynamics(user_input):
    amber = createAmber(user_input)
    if user_input.is_hpc:
        number_trajectories = 1
        directory = "mmground/restart_{}".format(user_input.restart_attempt)
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         user_input.job_name,
                                                         number_trajectories, directory)
    else:
        slurm_files = None
    return amber, slurm_files

def create_directories(restart_attempt):
    mkdir("mmground")
    restart_directory = "mmground/restart_{}".format(restart_attempt)
    mkdir(restart_directory)

def choose_restart(user_input):
    restart = user_input.restart_attempt
    desired_name = "snap_for_mm_r{}.rst".format(restart)
    if restart == 0:
        if user_input.is_qmmm:
            copy_file("./m1_md2.rst", desired_name)
        else:
            copy_file("./m1.inpcrd", desired_name)
    return desired_name

def copy_inputs(user_input, source_directory, output_directory):
    restart_file = choose_restart(user_input)
    basics = ["m1.prmtop", "input.ceon", restart_file]
    source_files = ["{}/{}".format(source_directory, b) for b in basics]
    output_files = ["{}/{}".format(output_directory, b) for b in basics]
    copy_files(source_files, output_files)

def choose_source_directory(restart_attempt):
    if restart_attempt == 0:
        return "."
    return "mmground/restart_{}".format(restart_attempt-1)

def create_restarts_from_parent(md_qmmm_amb, user_input):
    restart = user_input.restart_attempt
    create_directories(restart)
    setInput(md_qmmm_amb, user_input)
    source_directory = choose_source_directory(restart)
    output_directory = "mmground/restart_{}".format(restart)
    copy_inputs(user_input, source_directory, output_directory)

def isrestarting(user_input):
    if user_input.restart_attempt >= user_input.n_ground_runs - 1:
        return False
    return True

def islastrun(user_input):
    return not isrestarting(user_input)

def remove_partial_trajectories(n_runs):
    partial_trajs = ["mmground/restart_{}/nasqm_ground_r{}.nc".format(i, i)
                     for i in range(n_runs)]
    call = ['rm']
    call.extend(partial_trajs)
    subprocess.call(call)

def combine_trajectories(n_runs):
    trajs = ["mmground/restart_{}/nasqm_ground_r{}.nc".format(i, i)
             for i in range(n_runs)]
    prmtop = "mmground/restart_0/m1.prmtop"
    traj = pt.load(trajs, top=prmtop)
    pt.io.write_traj("mmground/nasqm_ground.nc", traj, velocity=True, overwrite=True)
    remove_partial_trajectories(n_runs)

def groundStateDynamics(md_qmmm_amb, user_input):
    create_restarts_from_parent(md_qmmm_amb, user_input)
    amber, slurm_files = prepareDynamics(user_input)
    runDynamics(user_input, amber, slurm_files)
    if islastrun(user_input):
        combine_trajectories(user_input.n_ground_runs)
