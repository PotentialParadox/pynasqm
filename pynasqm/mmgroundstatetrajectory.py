import subprocess
import functools
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm
import pytraj as pt

def setInput(md_qmmm_amb, user_input):
    input_ceon = md_qmmm_amb.copy("./", "nasqm_ground.in", True)
    input_ceon.set_n_steps(user_input.n_steps_gs)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_gmcrd)
    input_ceon.set_quantum(False)
    input_ceon.set_exc_state_propagate(0)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_gs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(0)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(True)

def createAmber(user_input):
    amber = Amber()
    amber.input_roots = ["nasqm_ground"]
    amber.output_roots = ["nasqm_ground"]
    amber.prmtop_files = ["m1.prmtop"]
    amber.restart_roots = ["nasqm_ground"]
    amber.export_roots = ["nasqm_ground"]
    if user_input.is_qmmm:
        amber.coordinate_files = ['m1_md2.rst']
    elif not user_input.is_qmmm:
        amber.coordinate_files = ['m1.inpcrd']
    else:
        amber.coordinate_files = ['nasqm_ground.rst']
    return amber

def runDynamics(user_input, amber, slurm_files):
    if user_input.is_hpc:
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
    else:
        amber.run_amber(number_processors=1, is_ground_state=True)

def prepareDynamics(md_qmmm_amb, user_input):
    setInput(md_qmmm_amb, user_input)
    amber = createAmber(user_input)
    if user_input.is_hpc:
        number_trajectories = 1
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         user_input.job_name,
                                                         number_trajectories)
    else:
        slurm_files = None
    return amber, slurm_files

def groundStateDynamics(md_qmmm_amb, user_input):
    amber, slurm_files = prepareDynamics(md_qmmm_amb, user_input)
    runDynamics(user_input, amber, slurm_files)
