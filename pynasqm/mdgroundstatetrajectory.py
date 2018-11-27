import subprocess
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm

def setInput(md_qmmm_amb, user_input, attempt):
    input_ceon = md_qmmm_amb.copy("./", "nasqm_ground_{}_{}.in".format(attempt+1, 1))
    input_ceon.set_n_steps(user_input.n_steps_gs)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_gmcrd)
    input_ceon.set_quantum(False)
    input_ceon.set_exc_state_propagate(0)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_gs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(0)
    input_ceon.set_time_step(user_input.time_step)
    if user_input.restart_attempt == 0:
        input_ceon.set_random_velocities(True)
    else:
        input_ceon.set_random_velocities(False)

def createAmber(user_input, attempt):
    amber = Amber()
    amber.input_roots = ["nasqm_ground_{}_".format(attempt+1)]
    amber.output_roots = ["nasqm_ground_{}_".format(attempt+1)]
    amber.prmtop_files = ["m1.prmtop"]
    amber.restart_roots = ["nasqm_ground_{}_".format(attempt+1)]
    amber.export_roots = ["nasqm_ground_{}_".format(attempt+1)]
    if user_input.is_qmmm and attempt == 0:
        amber.coordinate_files = ['m1_md2.rst']
    elif not user_input.is_qmmm and attempt == 0:
        amber.coordinate_files = ['m1.inpcrd']
    else:
        amber.coordinate_files = ['nasqm_ground_{}.rst'.format(attempt)]
    return amber

def copyNeededFiles(user_input, attempt):
    if user_input.is_qmmm and attempt == 0:
        subprocess.run(['cp', 'm1_md2.rst', 'm1_md2.rst.1'])

def runDynamics(user_input, amber):
    if user_input.is_hpc:
        number_trajectories = 1
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         amber.output_roots[0],
                                                         number_trajectories)
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
    else:
        amber.run_amber(number_processors=1, is_ground_state=True)

def moveFinalFiles(index):
        subprocess.run(['mv', 'nasqm_ground_{}_{}.out'.format(index, 1),
                        'nasqm_ground.out'])
        subprocess.run(['mv', 'nasqm_ground_{}_{}.nc'.format(index, 1),
                        'nasqm_ground.nc'])


def groundStateDynamics(md_qmmm_amb, user_input, attempt):
    setInput(md_qmmm_amb, user_input, attempt)
    copyNeededFiles(user_input, attempt)
    amber = createAmber(user_input, attempt)
    runDynamics(user_input, amber)
    if attempt + 1 == user_input.n_ground_runs:
        moveFinalFiles(attempt+1)
