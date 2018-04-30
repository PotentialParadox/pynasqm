'''
Run NASQM
created by Dustin Tracy (dtracy.uf@gmail.com)
This program is used to automate NASQM job creations.
You'll find the parameters to change in the file nasqm_user_input.py
'''
import time
import subprocess
from pynasqm.amber import Amber
from pynasqm.inputceon import InputCeon
from pynasqm.write import (write_omega_vs_time,
                           write_nasqm_flu_energie, write_spectra_flu_input,
                           write_spectra_abs_input)
from pynasqm.userinput import UserInput
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.absorptiontrajectories import AbsTrajectories
from pynasqm.fluorescencetrajectories import FluTrajectories


def main():
    '''
    The primary nasqm automation function call. All changable parameters can be
    found in nasqm_user_input.py
    '''

    user_input = UserInput()

    original_inputs = copy_inputs()
    input_ceon = create_input(user_input)

    start_time = time.time()

    input_ceon.set_n_steps_to_mcrd(userinput.n_steps_to_print_mcrd)
    if user_input.run_ground_state_dynamics:
        run_ground_state_dynamics(input_ceon, user_input)
    if user_input.run_absorption_trajectories:
        run_absorption_trajectories(input_ceon, user_input)
    if user_input.run_absorption_collection:
        run_absorption_collection(user_input)
    if user_input.run_excited_state_trajectories:
        run_excited_state_trajectories(input_ceon, user_input)
    if user_input.run_fluorescence_collection:
        run_fluorescence_collection(user_input)

    if not user_input.is_hpc:
        restore_inputs(original_inputs)
    input_ceon.write_log()

    end_time = time.time()
    print("Job finished in %s seconds" % (end_time - start_time))

def create_input(user_input):
    input_ceon = InputCeon(amber_input='md_qmmm_amb.in')
    input_ceon.set_periodic(user_input.is_qmmm, user_input.constant_value)
    return input_ceon

def copy_inputs():
    input_ceon_bac = open('input.ceon', 'r').read()
    md_qmmm_amb = open('md_qmmm_amb.in', 'r').read()
    return [input_ceon_bac, md_qmmm_amb]

def restore_inputs(origninal_inputs):
    open('input.ceon', 'w').write(origninal_inputs[0])
    open('md_qmmm_amb.in', 'w').write(origninal_inputs[1])

def create_inputceon_copies(input_ceon, root_name, number):
    '''
    Create an array of copies of the inputceons
    '''
    input_ceons = []
    for index in range(1, number+1):
        file_name = "{}{}.in".format(root_name, index)
        input_ceons.append(input_ceon.copy(file_name))
    return input_ceons

def run_ground_state_dynamics(input_ceon, user_input):
    '''
    Run the ground state trajectory that will be used to generate initial geometries
    for future calculations
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Ground State Trajectory !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_n_steps(user_input.n_steps_gs)
    input_ceon.set_quantum(False)
    input_ceon.set_exc_state_propagate(0)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_gs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(0)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(True)
    amber = Amber()
    amber.input_roots = ["md_qmmm_amb"]
    amber.output_roots = ["nasqm_ground"]
    amber.prmtop_files = ["m1.prmtop"]
    amber.restart_roots = ["nasqm_ground"]
    amber.export_roots = ["nasqm_ground"]
    if user_input.is_qmmm:
        amber.coordinate_files = ['m1_md2.rst']
    else:
        amber.coordinate_files = ['m1.inpcrd']
    if user_input.is_hpc:
        subprocess.run(['cp', 'md_qmmm_amb.in', 'md_qmmm_amb1.in'])
        if user_input.is_qmmm:
            subprocess.run(['cp', 'm1_md2.rst', 'm1_md2.rst.1'])
        else:
            subprocess.run(['cp', 'm1.inpcrd', 'm1.inpcrd.1'])
        number_trajectories = 1
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         amber.output_roots[0],
                                                         number_trajectories)
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
        subprocess.run(['mv', 'nasqm_ground1.out', 'nasqm_ground.out'])
        subprocess.run(['mv', 'nasqm_ground1.rst', 'nasqm_ground.rst'])
        subprocess.run(['mv', 'nasqm_ground1.nc', 'nasqm_ground.nc'])
        subprocess.run(['rm', 'md_qmmm_amb1.in'])
    else:
        amber.run_amber()

def run_absorption_trajectories(input_ceon, user_input):
    '''
    Now we want to take the original trajectory snapshots and run more trajectories
    using random velocities to make them different from each other
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Absorbance Trajectories !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_n_steps(user_input.n_steps_abs)
    input_ceon.set_quantum(True)
    input_ceon.set_exc_state_propagate(user_input.n_abs_exc)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_abs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(True)
    AbsTrajectories(user_input, input_ceon).run()

def run_absorption_collection(user_input):
    '''
    Parse the output data from amber for absorption energies and create a spectra_abs.input
    file
    '''
    print("!!!!!!!!!!!!!!!!!!!! Parsing Absorbance !!!!!!!!!!!!!!!!!!!!")
    write_spectra_abs_input(user_input)

def run_excited_state_trajectories(input_ceon, user_input):
    '''
    We take the original trajectory snapshots and run further trajectories
    from those at the excited state
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Excited States !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_quantum(True)
    input_ceon.set_n_steps(user_input.n_steps_exc)
    input_ceon.set_exc_state_propagate(user_input.n_exc_states_propagate_ex_param)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
    input_ceon.set_exc_state_init(user_input.exc_state_init_ex_param)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(False)
    FluTrajectories(user_input, input_ceon).run()

def run_fluorescence_collection(user_input):
    '''
    Parse the output data from amber for fluorescene energies and create a spectra_flu.input
    file
    '''
    print("!!!!!!!!!!!!!!!!!!!! Parsing Fluorescences !!!!!!!!!!!!!!!!!!!!")
    exc_state_init = user_input.exc_state_init_ex_param
    write_spectra_flu_input(user_input)
    write_omega_vs_time(n_trajectories=user_input.n_snapshots_ex, n_states=exc_state_init)
    write_nasqm_flu_energie(n_trajectories=user_input.n_snapshots_ex, n_states=exc_state_init)

main()
