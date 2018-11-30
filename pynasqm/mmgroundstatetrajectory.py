import subprocess
import functools
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm
import pytraj as pt

def setInput(md_qmmm_amb, user_input, attempt):
    input_ceon = md_qmmm_amb.copy("./", "nasqm_ground_r{}.in".format(attempt), True)
    input_ceon.set_n_steps(user_input.n_steps_gs)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_gmcrd)
    input_ceon.set_quantum(False)
    input_ceon.set_exc_state_propagate(0)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_gs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(0)
    input_ceon.set_time_step(user_input.time_step)
    if attempt == 0:
        input_ceon.set_random_velocities(True)
    else:
        input_ceon.set_random_velocities(False)

def createAmber(user_input, attempt):
    amber = Amber()
    amber.input_roots = ["nasqm_ground_r{}".format(attempt)]
    amber.output_roots = ["nasqm_ground_r{}".format(attempt)]
    amber.prmtop_files = ["m1.prmtop"]
    amber.restart_roots = ["nasqm_ground_r{}".format(attempt)]
    amber.export_roots = ["nasqm_ground_r{}".format(attempt)]
    if user_input.is_qmmm and attempt == 0:
        amber.coordinate_files = ['m1_md2.rst']
    elif not user_input.is_qmmm and attempt == 0:
        amber.coordinate_files = ['m1.inpcrd']
    else:
        amber.coordinate_files = ['nasqm_ground_r{}.rst'.format(attempt-1)]
    return amber

def runDynamics(user_input, amber, slurm_files):
    if user_input.is_hpc:
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
    else:
        amber.run_amber(number_processors=1, is_ground_state=True)

def combineFinalTrajs(index):
    trajectories = ["nasqm_ground_r{}.nc".format(i) for i in range(index+1)]
    traj = pt.load(trajectories, top='m1.prmtop')
    pt.io.write_traj('nasqm_ground.nc', traj, velocity=True, overwrite=True)

def removeSplitTrajs(index):
    pass
    # for i in range(index+1):
    #     subprocess.call(['rm','nasqm_ground_r{}.nc'.format(i)])
    #     subprocess.call(['rm','nasqm_ground_r{}.rst'.format(i)])

def prepareDynamics(md_qmmm_amb, user_input, attempt):
    setInput(md_qmmm_amb, user_input, attempt)
    amber = createAmber(user_input, attempt)
    if user_input.is_hpc:
        number_trajectories = 1
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         user_input.job_name,
                                                         number_trajectories)
    else:
        slurm_files = None
    return amber, slurm_files

def groundStateDynamics(md_qmmm_amb, user_input, attempt):
    amber, slurm_files = prepareDynamics(md_qmmm_amb, user_input, attempt)
    runDynamics(user_input, amber, slurm_files)
    if attempt + 1 == user_input.n_ground_runs:
        combineFinalTrajs(attempt)
        removeSplitTrajs(attempt)
