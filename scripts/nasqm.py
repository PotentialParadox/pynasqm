'''
Run NASQM
created by Dustin Tracy (dtracy.uf@gmail.com)
This program is used to automate NASQM job creations.
You'll find the parameters to change in the file nasqm_user_input.py
'''
import argparse
import time
from pynasqm.inputceon import InputCeon
from pynasqm.write import (write_omega_vs_time,
                           write_nasqm_flu_energie, write_spectra_flu_input,
                           write_spectra_abs_input, write_average_coeffs)
from pynasqm.userinput import UserInput
from pynasqm.absorptiontrajectories import AbsTrajectories
from pynasqm.fluorescencetrajectories import FluTrajectories
from pynasqm.initialexcitedstates import get_energies_and_strenghts
from pynasqm.mmgroundstatetrajectory import groundStateDynamics


def main():
    '''
    The primary nasqm automation function call. All changable parameters can be
    found in userinput.py
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("--job", help="0-ground, 1-abs, 2-flu", default=0, type=int)
    parser.add_argument("--restart", help="restart attempt, 0 for first run", default=0, type=int)
    args = parser.parse_args()

    user_input = UserInput()
    user_input.restart_attempt = args.restart

    if args.restart != 0:
        if args.job > 0:
            user_input.run_ground_state_dynamics = False
        if args.job > 1:
            user_input.run_absorption_trajectories = False
            user_input.run_absorption_collection = False

    original_inputs = copy_inputs()
    input_ceon = create_input(user_input)

    start_time = time.time()

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
    input_ceon = InputCeon(amber_input='md_qmmm_amb.in', directory='./')
    input_ceon.set_periodic(user_input.is_qmmm, user_input.constant_value)
    return input_ceon

def copy_inputs():
    input_ceon_bac = open('input.ceon', 'r').read()
    md_qmmm_amb = open('md_qmmm_amb.in', 'r').read()
    return [input_ceon_bac, md_qmmm_amb]

def restore_inputs(origninal_inputs):
    open('input.ceon', 'w').write(origninal_inputs[0])
    open('md_qmmm_amb.in', 'w').write(origninal_inputs[1])

def run_ground_state_dynamics(md_qmmm_amb, user_input):
    '''
    Run the ground state trajectory that will be used to generate initial geometries
    for future calculations
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Ground State Trajectory !!!!!!!!!!!!!!!!!!!!")
    for attempt in range(user_input.restart_attempt, user_input.n_ground_runs):
        groundStateDynamics(md_qmmm_amb, user_input, attempt)

def run_absorption_trajectories(input_ceon, user_input):
    '''
    Now we want to take the original trajectory snapshots and run more trajectories
    using random velocities to make them different from each other
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Absorbance Trajectories !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_n_steps(user_input.n_steps_abs)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_amcrd)
    input_ceon.set_quantum(True)
    input_ceon.set_excited_state(0, user_input.n_abs_exc)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_abs)
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
    energies, strengths = get_energies_and_strenghts('spectra_abs.input')
    print_energies_and_strengths(energies, strengths)

def print_energies_and_strengths(energies, strengths):
    print('Energies and Strengths')
    for i, (e, s) in enumerate(zip(energies, strengths)):
        print('State {}: Energy: {}, Strength: {}'.format(i+1, e, s))

def run_excited_state_trajectories(input_ceon, user_input):
    '''
    We take the original trajectory snapshots and run further trajectories
    from those at the excited state
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Excited States !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_quantum(True)
    input_ceon.set_n_steps(user_input.n_steps_exc)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
    input_ceon.set_excited_state(user_input.exc_state_init_ex_param,
                                 user_input.n_exc_states_propagate_ex_param)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(False)
    input_ceon.set_bo(user_input.is_tully, user_input.qsteps)
    FluTrajectories(user_input, input_ceon).run()

def run_fluorescence_collection(user_input):
    '''
    Parse the output data from amber for fluorescene energies and create a spectra_flu.input
    file
    '''
    print("!!!!!!!!!!!!!!!!!!!! Parsing Fluorescences !!!!!!!!!!!!!!!!!!!!")
    exc_state_init = user_input.exc_state_init_ex_param
    exc_state_prop = user_input.n_exc_states_propagate_ex_param
    write_spectra_flu_input(user_input)
    write_omega_vs_time(n_trajectories=user_input.n_snapshots_ex, n_states=exc_state_init)
    write_nasqm_flu_energie(n_trajectories=user_input.n_snapshots_ex, n_states=exc_state_init)
    if (user_input.is_tully):
        write_average_coeffs(n_trajectories=user_input.n_snapshots_ex, n_states=exc_state_prop)

main()
