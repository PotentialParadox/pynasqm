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
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.closestrunner import ClosestRunner
from pynasqm.solventmaskupdater import SolventMaskUpdater
from pynasqm.nmrmanager import NMRManager


def run_nasqm(root_name, coordinate_file=None, pmemd_available=False):
    '''
    Command line command to call nasqm
    '''
    cd_file = 'm1.inpcrd'
    if coordinate_file is not None:
        cd_file = coordinate_file
    amber = 'sander'
    if pmemd_available:
        amber = 'pmemd.cuda'
    subprocess.run([amber, '-O', '-i', 'md_qmmm_amb.in', '-o', root_name+'.out', '-c',
                    cd_file, '-p', 'm1.prmtop', '-r', root_name+'.rst', '-x', root_name+'.nc'])

def create_inputceon_copies(input_ceon, root_name, number):
    '''
    Create an array of copies of the inputceons
    '''
    input_ceons = []
    for index in range(1, number+1):
        file_name = "{}{}.in".format(root_name, index)
        input_ceons.append(input_ceon.copy(file_name))
    return input_ceons

def run_simulation_from_trajectory(nasqm_root, output_root, n_frames_in_oringinal, n_new_trajectories,
                                   user_input, input_ceon):
    '''
    Run n_new_trajectories simulations using nasqm_root as the basis for the generation of the
    inital geometries. This will output data to output_root+str(i). Restart_step is the
    number of steps between the snapshots of the trajectory you are using as your geometries
    generator.
    '''
    restart_step = int(n_frames_in_oringinal / n_new_trajectories)
    amber_restart_root = 'ground_snap'
    nasqm_cpptraj.create_restarts(amber_input=nasqm_root,
                                  output=amber_restart_root, step=restart_step)
    input_ceons = create_inputceon_copies(input_ceon, output_root, n_new_trajectories)
    closest_runner = ClosestRunner(user_input.number_nearest_solvents, n_new_trajectories,
                                   user_input.mask_for_center)
    closest_outputs = closest_runner.create_closest_outputs()
    mask_updater = SolventMaskUpdater(input_ceons, user_input, closest_outputs)
    mask_updater.update_masks()
    if user_input.desired_distance != None:
        NMRManager(input_ceons, user_input, closest_outputs).update()

    if user_input.is_hpc:
        if n_new_trajectories == 1:
            subprocess.run(['mv', 'ground_snap', 'ground_snap.1'])
        amber = Amber()
        amber.input_roots = [output_root]
        amber.output_roots = [output_root]
        amber.coordinate_files = [amber_restart_root]
        amber_calls_per_trajectory = 1
        if output_root == 'nasqm_abs_':
            job_suffix = '_a_'
        elif output_root == 'nasqm_flu_':
            job_suffix = '_f_'
        job_name = user_input.job_name + "_" + job_suffix
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         job_name, n_new_trajectories,
                                                         amber_calls_per_trajectory)
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
    else:
        snap_restarts = []
        trajectory_roots = []
        if n_new_trajectories == 1:
            snap_restarts.append(amber_restart_root)
            trajectory_roots.append(output_root + '1')
        else:
            for i in range(n_new_trajectories):
                snap_restarts.append(amber_restart_root+"."+str(i+1))
                trajectory_roots.append(output_root + str(i + 1))
        amber = Amber()
        amber.input_roots = trajectory_roots
        amber.output_roots = trajectory_roots
        amber.coordinate_files = snap_restarts
        amber.prmtop_files = ["m1.prmtop"]*len(trajectory_roots)
        amber.restart_roots = trajectory_roots
        amber.export_roots = trajectory_roots
        amber.run_amber(user_input.processors_per_node)

def run_flu_from_abs(output_root, n_new_trajectories, user_input, input_ceon):
    '''
    Run n_new_trajectories simulations using nasqm_root as the basis for the generation of the
    inital geometries. This will output data to output_root+str(i). Restart_step is the
    number of steps between the snapshots of the trajectory you are using as your geometries
    generator.
    '''
    amber_restart_root = 'nasqm_abs_'
    input_ceons = create_inputceon_copies(input_ceon, output_root, n_new_trajectories)
    closest_runner = ClosestRunner(user_input.number_nearest_solvents, n_new_trajectories,
                                   user_input.mask_for_center)
    closest_outputs = closest_runner.create_closest_outputs()
    mask_updater = SolventMaskUpdater(input_ceons, user_input, closest_outputs)
    mask_updater.update_masks()
    if user_input.desired_distance != None:
        NMRManager(input_ceons, user_input, closest_outputs).update()
    if user_input.is_hpc:
        amber = Amber()
        amber.input_roots = [output_root]
        amber.output_roots = [output_root]
        amber.coordinate_files = [amber_restart_root]
        amber.from_restart = True
        amber_calls_per_trajectory = 1
        if output_root == 'nasqm_abs_':
            job_suffix = '_a_'
        elif output_root == 'nasqm_flu_':
            job_suffix = '_f_'
        job_name = user_input.job_name + job_suffix
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         job_name, n_new_trajectories,
                                                         amber_calls_per_trajectory)
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
    else:
        snap_restarts = []
        trajectory_roots = []
        if n_new_trajectories == 1:
            snap_restarts.append("{}{}.rst".format(amber_restart_root, 1))
            trajectory_roots.append("{}{}".format(output_root, 1))
        else:
            for i in range(n_new_trajectories):
                snap_restarts.append("{}{}.rst".format(amber_restart_root, str(i+1)))
                trajectory_roots.append(output_root + str(i + 1))
        amber = Amber()
        amber.input_roots = trajectory_roots
        amber.output_roots = trajectory_roots
        amber.coordinate_files = snap_restarts
        amber.prmtop_files = ["m1.prmtop"]*len(trajectory_roots)
        amber.restart_roots = trajectory_roots
        amber.export_roots = trajectory_roots
        amber.run_amber(user_input.processors_per_node)


def create_amber_inputs_abs_snaps(n_trajectories, n_frames):
    '''
    Create the amber input files for abs snapshots
    '''
    amber_inputs = []
    for traj_index in range(1, n_trajectories+1):
        for _ in range(n_frames):
            amber_inputs.append("nasqm_abs_{}".format(traj_index))
    return amber_inputs

def run_abs_snapshots(n_trajectories, n_frames, user_input, input_ceon):
    '''
    Run snapshots on the nasqm_abs_* ground state trajectory runs
    '''
    # input_ceons = create_inputceon_copies(input_ceon, "nasqm_abs_", n_trajectories)
    # update_closest(user_input, input_ceons)
    nasqm_abs = "nasqm_abs_"
    amber_inputs = create_amber_inputs_abs_snaps(n_trajectories, n_frames)
    input_ceons = create_inputceon_copies(input_ceon, nasqm_abs, n_trajectories)
    closest_runner = ClosestRunner(user_input.number_nearest_solvents, n_trajectories,
                                   user_input.mask_for_center)
    closest_outputs = closest_runner.create_closest_outputs()
    mask_updater = SolventMaskUpdater(input_ceons, user_input, closest_outputs)
    mask_updater.update_masks()
    if user_input.desired_distance != None:
        NMRManager(input_ceons, user_input, closest_outputs).update()
    for i in input_ceons:
        i.set_n_steps(0)
    for i in range(n_trajectories):
        amber_restart = nasqm_abs + str(i+1)
        nasqm_cpptraj.create_restarts(amber_input=amber_restart, output=amber_restart)
    # We will now have files that look like nasqm_abs_[trajectory]_[frame]
    # Lets run it
    snap_singles = []
    snap_restarts = []
    for traj in range(n_trajectories):
        for frame in range(n_frames):
            snap_singles.append(nasqm_abs + str(traj+1) + "_" + str(frame+1))
            snap_restarts.append(nasqm_abs + str(traj+1) + "." + str(frame+1))
    if user_input.is_hpc:
        amber = Amber()
        amber.input_roots = [nasqm_abs]
        amber.output_roots = [nasqm_abs]
        amber.coordinate_files = [nasqm_abs]
        amber_calls_per_trajectory = n_frames
        job_name = user_input.job_name + "_ac_"
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         job_name, n_trajectories,
                                                         amber_calls_per_trajectory)
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)
    else:
        amber = Amber()
        amber.input_roots = amber_inputs
        amber.output_roots = snap_singles
        amber.coordinate_files = snap_restarts
        amber.prmtop_files = ["m1.prmtop"]*len(snap_singles)
        amber.restart_roots = snap_singles
        amber.export_roots = snap_singles
        amber.run_amber(user_input.processors_per_node)


def clean_up_abs(is_tully, n_trajectories, n_frame):
    '''
    Removes the files created by the absorption routine
    '''
    base_name = 'nasqm_abs_'
    if is_tully:
        for i in range(n_trajectories):
            for j in range(n_frame):
                traj = i + 1
                frame = j + 1
                subprocess.run(['rm', base_name + str(traj) + '_' + str(frame) + '.out'])
                subprocess.run(['rm', base_name + str(traj) + '_' + str(frame) + '.nc'])
                subprocess.run(['rm', base_name + str(traj) + '_' + str(frame) + '.rst'])
                subprocess.run(['rm', base_name + str(traj) + '.' + str(frame)])
    else:
        subprocess.run('rm nasqm_abs_*', shell=True)
        subprocess.run('rm ground_snap*', shell=True)


def run_ground_state_dynamics(input_ceon, user_input):
    '''
    Run the ground state trajectory that will be used to generate initial geometries
    for future calculations
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Ground State Trajectory !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_n_steps(user_input.n_steps_gs)
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
        amber_calls_per_trajectory = 1
        slurm_files = nasqm_slurm.slurm_trajectory_files(user_input, amber,
                                                         amber.output_roots[0],
                                                         number_trajectories,
                                                         amber_calls_per_trajectory)
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
    input_ceon.set_exc_state_propagate(user_input.n_abs_exc)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_abs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(True)
    run_simulation_from_trajectory('nasqm_ground', 'nasqm_abs_', user_input.n_frames_gs,
                                   user_input.n_snapshots_gs, user_input, input_ceon)

def run_absorption_snapshots(input_ceon, user_input):
    '''
    Once the ground state trajectory file are made, we need can calculate the absorption
    snapshots.
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Absorbance Snapshots !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_n_steps(0)
    input_ceon.set_exc_state_propagate(user_input.n_abs_exc)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_abs)
    input_ceon.set_exc_state_init(0)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.time_step)
    run_abs_snapshots(n_trajectories=user_input.n_snapshots_gs,
                      n_frames=user_input.n_frames_abs, user_input=user_input,
                      input_ceon=input_ceon)

def run_absorption_collection(user_input):
    '''
    Parse the output data from amber for absorption energies and create a spectra_abs.input
    file
    '''
    print("!!!!!!!!!!!!!!!!!!!! Parsing Absorbance !!!!!!!!!!!!!!!!!!!!")
    write_spectra_abs_input(user_input)
    # clean_up_abs(user_input.is_tully, user_input.n_snapshots_gs, user_input.n_frames_abs)


def run_excited_state_trajectories(input_ceon, user_input):
    '''
    We take the original trajectory snapshots and run further trajectories
    from those at the excited state
    '''
    print("!!!!!!!!!!!!!!!!!!!! Running Excited States !!!!!!!!!!!!!!!!!!!!")
    input_ceon.set_n_steps(user_input.n_steps_exc)
    input_ceon.set_exc_state_propagate(user_input.n_exc_states_propagate_ex_param)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
    input_ceon.set_exc_state_init(user_input.exc_state_init_ex_param)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.time_step)
    input_ceon.set_random_velocities(False)
    output_root = "nasqm_flu_"
    run_flu_from_abs(output_root, user_input.n_snapshots_ex, user_input, input_ceon)

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
    subprocess.run('rm ground_snap*', shell=True)


def main():
    '''
    The primary nasqm automation function call. All changable parameters can be
    found in nasqm_user_input.py
    '''

    user_input = UserInput()

    # Copy inputs
    input_ceon_bac = open('input.ceon', 'r').read()
    md_qmmm_amb = open('md_qmmm_amb.in', 'r').read()
    m1_inpcrd = open('m1.inpcrd', 'r').read()

    # Create the input_ceon object
    input_ceon = InputCeon(amber_input='md_qmmm_amb.in')
    input_ceon.set_periodic(user_input.is_qmmm, user_input.constant_value)

    start_time = time.time()

    if user_input.run_ground_state_dynamics:
        run_ground_state_dynamics(input_ceon, user_input)
    if user_input.run_absorption_trajectories:
        run_absorption_trajectories(input_ceon, user_input)
    if user_input.run_absorption_snapshots:
        run_absorption_snapshots(input_ceon, user_input)
    if user_input.run_absorption_collection:
        run_absorption_collection(user_input)
    if user_input.run_excited_state_trajectories:
        run_excited_state_trajectories(input_ceon, user_input)
    if user_input.run_fluorescence_collection:
        run_fluorescence_collection(user_input)

    # Restore Original Inputs
    if not user_input.is_hpc:
        open('input.ceon', 'w').write(input_ceon_bac)
        open('md_qmmm_amb.in', 'w').write(md_qmmm_amb)
        open('m1.inpcrd', 'w').write(m1_inpcrd)
    input_ceon.write_log()

    end_time = time.time()
    print("Job finished in %s seconds" % (end_time - start_time))

main()

