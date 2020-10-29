'''
Run NASQM
created by Dustin Tracy (dtracy.uf@gmail.com)
This program is used to automate NASQM job creations.
You'll find the parameters to change in the file nasqm_user_input.py
'''
import argparse
import time
from pynasqm.initialize import initialize
from pynasqm.inputceon import InputCeon
from pynasqm.write import (write_omega_vs_time, write_spectra_flu_input,
                           write_average_coeffs)
from pynasqm.spectracollection import write_spectra_input
from pynasqm.userinput import UserInput
from pynasqm.trajectories.qmgroundstatetrajectories import QmGroundTrajectories
from pynasqm.trajectories.qmexcitedstatetrajectories import QmExcitedStateTrajectories
from pynasqm.trajectories.pulsepump import PulsePump
from pynasqm.initialexcitedstates import get_energies_and_strenghts
from pynasqm.trajectories.mmgroundstatetrajectory import groundStateDynamics
from pynasqm.trajectories.absorptionsnaps import AbsorptionSnaps
from pynasqm.trajectories.fluorescencesnaps import FluorescenceSnaps
from pynasqm.sed import sed_inplace, sed_global
from pynasqm.nasqmslurm import restart_nasqm
from pynasqm.trajectories.combine_trajectories import combine_trajectories
from pynasqm.collect_coeffs import collect_coeffs
import subprocess


def main():
    '''
    The primary nasqm automation function call. All changable parameters can be
    found in userinput.py
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("--init", help="initialize the directory for nasqm", action="store_true")
    parser.add_argument("--job", help="0-ground, 1-qmground, 2-qmexcited", default=0, type=int)
    parser.add_argument("--restart", help="restart attempt, 0 for first run", default=0, type=int)
    args = parser.parse_args()

    if args.init:
        title_print('Initializing Directory')
        print("Amber Input File: md_qmmm_amb.in")
        print("NEXMD Input File: input.ceon")
        print("PYNASQM Input File: pynasqm.in")
        print("Please rename your coordinate file to m1_md2.rst")
        print("Please rename your parmtop file to m1.prmtop")
        initialize()
        exit()

    user_input = UserInput()
    user_input.restart_attempt = args.restart

    if args.restart != 0:
        if args.job > 0:
            user_input.run_ground_state_dynamics = False
        if args.job > 1:
            user_input.run_qmground_trajectories = False
            user_input.run_absorption_collection = False

    original_inputs = copy_inputs()
    input_ceon = create_input(user_input)

    start_time = time.time()

    if user_input.run_ground_state_dynamics:
        run_mm_ground_state_dynamics(input_ceon, user_input)
    if user_input.run_qmground_trajectories:
        run_qm_ground_state_trajectories(input_ceon, user_input)
    if user_input.run_absorption_snapshots:
        run_absorption_snaps(input_ceon, user_input)
    if user_input.run_absorption_collection:
        run_absorption_collection(user_input)
    if should_perform_pulse_pump(user_input, args.restart):
        run_pulse_pump_prep(input_ceon, user_input)
    if should_perform_pulse_pump_collection(user_input, args.restart):
        run_pulse_pump_prep_collection(input_ceon, user_input)
    if user_input.run_excited_state_trajectories:
        run_excited_state_trajectories(input_ceon, user_input)
    if user_input.run_fluorescence_snapshots:
        run_fluorescence_snaps(input_ceon, user_input)
    if user_input.run_fluorescence_collection:
        run_fluorescence_collection(user_input)

    if not user_input.is_hpc:
        restore_inputs(original_inputs)
    input_ceon.write_log()

    end_time = time.time()
    print("Job finished in %s seconds" % (end_time - start_time))

def should_perform_pulse_pump(user_input, restart):
    return (
        user_input.run_pulse_pump_singlepoints and
        restart == 0
    )

def should_perform_pulse_pump_collection(user_input, restart):
    return (
        user_input.run_pulse_pump_collection and
        restart == 0
    )

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

def should_restart(n_runs, restart_attempt):
    if restart_attempt + 1 >= n_runs:
        return False
    return True

def restart(user_input, job_id, restart_attempt):
    if user_input.is_hpc:
        restart_nasqm(user_input, job_id, restart_attempt)
    else:
        restart_for_pc(job_id, restart_attempt)
    exit()

def restart_for_pc(job_id, restart_attempt):
    subprocess.call(["nasqm.py", "--job", "{}".format(job_id),
                     "--restart", "{}".format(restart_attempt)])

def manage_restart(job_id, user_input, restart_attempt):
    runs = [user_input.n_ground_runs, user_input.n_qmground_runs, user_input.n_exc_runs]
    n_runs = runs[job_id]
    job_desciption = ["mmground", "qmground", "qmexcited"]
    if should_restart(n_runs, restart_attempt):
        print(f"restarting with {job_desciption[job_id]}\n")
        restart(user_input, job_id, restart_attempt+1)
    user_input.restart_attempt = 0

def title_print(label):
    break_width = 80
    offset = int(break_width/2) - int(len(label)/2)
    break_line = "!"*break_width + "\n"
    info_line = "!" + " "*offset + label + "\n"
    print(break_line + info_line + break_line)


def run_mm_ground_state_dynamics(md_qmmm_amb, user_input):
    '''
    Run the ground state trajectory that will be used to generate initial geometries
    for future calculations
    '''
    title_print("MM Ground-State Trajectory")
    groundStateDynamics(md_qmmm_amb, user_input)
    manage_restart(0, user_input, user_input.restart_attempt)


def run_qm_ground_state_trajectories(input_ceon, user_input):
    '''
    Now we want to take the original trajectory snapshots and run more trajectories
    using random velocities to make them different from each other
    '''
    title_print("QM Ground-State Trajectories")
    QmGroundTrajectories(user_input, input_ceon).run()
    manage_restart(1, user_input, user_input.restart_attempt)

def run_absorption_snaps(input_ceon, user_input):
    '''
    Take snapshots from the qmground trajectories ignoring a time delay.
    Run singlepoints on these snaphsots
    '''
    title_print("Absorption Snaps")
    AbsorptionSnaps(user_input, input_ceon).run()

def run_absorption_collection(user_input):
    '''
    Parse the output data from amber for absorption energies and create a spectra_abs.input
    file
    '''
    title_print("Absorption Parsing")
    write_spectra_input(user_input, 'absorption')
    energies, strengths = get_energies_and_strenghts('spectra_absorption.input')
    print_energies_and_strengths(energies, strengths)

def print_energies_and_strengths(energies, strengths):
    with open('absorption_summary.txt', 'w') as fout:
        fout.write('Energies and Strengths\n')
        for i, (e, s) in enumerate(zip(energies, strengths)):
            fout.write('State {}: Energy:{:14.10f}, Strength: {:14.10f}\n'.format(i+1, e, s))

def run_pulse_pump_prep(input_ceon, user_input):
    title_print("Performing  Pulse Pump Single Points")
    PulsePump(user_input, input_ceon).run()

def run_pulse_pump_prep_collection(input_ceon, user_input):
    title_print("Performing  Pulse Pump Collection")
    PulsePump(user_input, input_ceon).write_pulse_pump_states()
    write_spectra_input(user_input, 'pulse_pump')

def run_excited_state_trajectories(input_ceon, user_input):
    '''
    We take the original trajectory snapshots and run further trajectories
    from those at the excited state
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Excited States !!!!!!!!!!!!!!!!!!!!")
    QmExcitedStateTrajectories(user_input, input_ceon).run()
    manage_restart(2, user_input, user_input.restart_attempt)
    if user_input.is_tully:
        collect_coeffs(
            number_trajectories=user_input.n_snapshots_ex,
            number_restarts=user_input.n_exc_runs - 1
        )

def run_fluorescence_snaps(input_ceon, user_input):
    '''
    Take snapshots from the qmground trajectories ignoring a time delay.
    Run singlepoints on these snaphsots
    '''
    title_print("Fluorescence Snaps")
    FluorescenceSnaps(user_input, input_ceon).run()

def run_fluorescence_collection(user_input):
    '''
    Parse the output data from amber for fluorescene energies and create a spectra_flu.input
    file
    '''
    print("!!!!!!!!!!!!!!!!!!!! Parsing Fluorescences !!!!!!!!!!!!!!!!!!!!")
    combine_trajectories("flu", user_input.n_snapshots_ex, user_input.n_exc_runs)
    exc_state_init = user_input.exc_state_init_ex_param
    exc_state_prop = user_input.n_exc_states_propagate_ex_param
    n_completed = write_spectra_flu_input(user_input)
    write_omega_vs_time(n_trajectories=n_completed, n_states=exc_state_init)
    if user_input.is_tully:
        write_average_coeffs(n_trajectories=user_input.n_snapshots_ex, n_states=exc_state_prop)

try:
    main()
except KeyboardInterrupt:
    print("You canceled the operation")
