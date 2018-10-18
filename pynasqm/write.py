"""
Functions that write outputs of the NASQM script
"""
import subprocess
import statistics
import io
import numpy as np
import pynasqm.utils
from pynasqm.amberout import find_nasqm_excited_state, find_excited_energies
from pynasqm.coeffreader import get_coeffs, get_times
import re


def numpy_to_specta_string(numpy_data):
    '''
    Converts a numpy array into the string used in spectra.input files
    '''
    string_output = ''
    for data in numpy_data:
        string_output += "{: 24.14E}{: 24.14E}".format(data[0], data[1]) + "\n"
    return string_output


def strip_timedelay(spectra_string, n_trajectories, time_step, time_delay, ntpr=1):
    '''
    Remove the data from the equilibration time given by time_delay
    Time is in fs
    '''
    row1 = spectra_string.split('\n', 1)[0]
    row1_data = np.fromstring(row1, sep=" ")
    n_columns = len(row1_data)
    data = np.fromstring(spectra_string, sep=" ")
    n_rows = int(len(data) / n_columns)
    n_elements_traj = int(n_rows / n_trajectories)
    data = data.reshape((n_rows, n_columns))
    n_rows_to_remove_traj = int(time_delay / (time_step*ntpr))
    n_rows_to_remove = n_rows_to_remove_traj * n_trajectories
    n_rows_data2 = n_rows - n_rows_to_remove
    if n_rows_data2 < 0:
        raise ValueError('Time delay greater than the excited state runtime.')
    data2 = np.zeros((n_rows_data2, n_columns))
    data2_ri = 0
    for i, data_point in enumerate(data):
        if i % n_elements_traj >= n_rows_to_remove_traj:
            data2[data2_ri][:] = data_point[:]
            data2_ri += 1
    answer = pynasqm.utils.numpy_to_txt(data2, form="scientific")
    return answer

def truncate_spectra(spectra_string, n_trajectories, time_step, time_delay, ntpr=1):
    '''
    Truncate the spectra by a given time
    Time is in fs
    '''
    row1 = spectra_string.split('\n', 1)[0]
    row1_data = np.fromstring(row1, sep=" ")
    n_columns = len(row1_data)
    data = np.fromstring(spectra_string, sep=" ")
    n_rows = int(len(data) / n_columns)
    n_elements_traj = int(n_rows / n_trajectories)
    data = data.reshape((n_rows, n_columns))
    n_rows_to_remove_traj = int(time_delay / (time_step*ntpr))
    n_rows_to_remove = n_rows_to_remove_traj * n_trajectories
    n_rows_data2 = n_rows - n_rows_to_remove
    if n_rows_data2 < 0:
        raise ValueError('Truncation time greater than the excited state runtime minus time delay.')
    data2 = np.zeros((n_rows_data2, n_columns))
    data2_ri = 0
    for i, data_point in enumerate(data):
        if i % n_elements_traj < n_elements_traj - n_rows_to_remove_traj:
            data2[data2_ri][:] = data_point[:]
            data2_ri += 1
    answer = pynasqm.utils.numpy_to_txt(data2, form="scientific")
    return answer

def traj_finished(amber_outfile):
    '''
    Checks to see if the amber output file finished without
    '''
    lines = open(amber_outfile, 'r').readlines()
    if "Could not go further" in lines[-1]:
        return False
    return True

def print_failed(failed_trajs):
    if failed_trajs == []:
        return ""
    failed_string = "Trajectories: "
    for traj in failed_trajs:
        failed_string += "{} ".format(traj)
    failed_string += "failed and are being skipped in the calculation of flu spectra"
    print(failed_string)

def accumulate_flu_spectra(n_trajectories, n_states=10):
    """
    Create the spectra_flu.input file using the nasqm_flu_*.out files
    """
    output_stream = io.StringIO()
    failed_jobs = []
    for i in range(n_trajectories):
        amber_outfile = '{}/nasqm_flu_{}.out'.format(i+1, i+1)
        input_stream = open(amber_outfile, 'r')
        if traj_finished(amber_outfile):
            find_nasqm_excited_state(input_stream, output_stream,
                                     states=[j for j in range(1, n_states+1)])
        else:
            failed_jobs.append(i+1)
        input_stream.close()
    print_failed(failed_jobs)
    output_string = output_stream.getvalue()
    output_stream.close()
    return output_string

def accumulate_abs_spectra(n_snapshots_gs, n_frames, n_states=20):
    '''
    Reads the data from the amber output files and writes the data to spectra_abs.input
    '''
    output_stream = io.StringIO()
    for i in range(n_snapshots_gs):
        amber_outfile = '{}/nasqm_abs_{}.out'.format(i+1, i+1)
        input_stream = open(amber_outfile, 'r')
        find_nasqm_excited_state(input_stream, output_stream, states=[j for j in range(1, n_states+1)])
        input_stream.close()
    output_string = output_stream.getvalue()
    output_stream.close()
    return output_string

def write_spectra_abs_input(user_input):
    '''
    Writes the approriately formatted data to spectra_abs.input.
    Use hist_spectra_lifetime, and naesmd_spectra_plotter to get the spectra.
    '''
    abs_string = accumulate_abs_spectra(user_input.n_snapshots_gs, user_input.n_frames_abs,
                                        user_input.n_abs_exc)
    time_step = user_input.time_step * user_input.n_steps_to_print_gs
    abs_string = strip_timedelay(abs_string, user_input.n_snapshots_gs, time_step,
                                 user_input.abs_time_delay, user_input.n_steps_to_print_abs)
    open('spectra_abs.input', 'w').write(abs_string)

def write_spectra_flu_input(user_input):
    '''
    Writes the approriately formatted data to spectra_flu.input.
    Use hist_spectra_lifetime, and naesmd_spectra_plotter to get the spectra.
    '''
    fluor_string = accumulate_flu_spectra(n_trajectories=user_input.n_snapshots_ex,
                                          n_states=user_input.n_exc_states_propagate_ex_param)
    # The timestep needs to be adjusted for the number of frames skipped
    time_step = user_input.time_step * user_input.n_steps_to_print_exc
    fluor_string = strip_timedelay(fluor_string, user_input.n_snapshots_ex,
                                   time_step,
                                   user_input.fluorescence_time_delay,
                                   user_input.n_steps_to_print_exc)
    fluor_string = truncate_spectra(fluor_string, user_input.n_snapshots_ex,
                                          time_step,
                                          user_input.fluorescence_time_truncation,
                                          user_input.n_steps_to_print_exc)
    open('spectra_flu.input', 'w').write(fluor_string)

def coeff_error_string(unlike):
    error_string = "Unlike Coefficients in trajectories: "
    for u in unlike:
        error_string += "{} ".format(u+1)
    error_string += "\nSkipping these in the calculations of populations"
    return error_string

def verify_coeffs(coeffs):
    counts = [len(x) for x in coeffs]
    mode = statistics.mode(counts)
    unlike = [i for i, x in enumerate(counts) if x != mode]
    if unlike != []:
        print(coeff_error_string(unlike))
    acceptable = [i for i, x in enumerate(counts) if x == mode]
    if acceptable == []:
        raise ValueError('No trajectories finished')
    return acceptable

def write_average_coeffs(n_trajectories, n_states=1):
    N = n_trajectories
    filenames = ["{}/coeff-n.out".format(x) for x in range(1, N+1)]
    coeffs = np.array([get_coeffs(f) for f in filenames])
    completed_trajectories = verify_coeffs(coeffs)
    coeffs = [coeffs[x] for x in completed_trajectories]
    n_steps = len(coeffs[0])
    times = np.array([get_times(f) for f in filenames])
    times = [times[x] for x in completed_trajectories]
    coeff_average = np.average(coeffs, axis=0)
    print_values = np.zeros((n_steps, n_states+1))
    print_values[:,0] = times[0]
    print_values[:,1:] = coeff_average
    np.savetxt('average_coefficient.out', print_values)

def write_omega_vs_time(n_trajectories, n_states=1):
    '''
    Reads data from spectra_flu.input and writes the omegas vs time
    to omega_1_time.txt
    '''
    average_omegas_time = open('omega_1_time.txt', 'w')
    data = np.loadtxt('spectra_flu.input')
    n_rows_per_trajectory = int(data.shape[0] / n_trajectories)
    for i in range(n_rows_per_trajectory):
        omega = np.average(data[i::n_rows_per_trajectory, 0])
        average_omegas_time.write(str(omega) + '\n')
    average_omegas_time.close()


def write_nasqm_flu_energie(n_trajectories, n_states=1):
    '''
    Reads the data from the amber output files and writes the data
    to nasqm_flue_energies.txt
    '''
    state_range = range(1, n_states+1)
    output_stream = open('nasqm_flu_energies.txt', 'w')
    for i in range(n_trajectories):
        amber_outfile = '{}/nasqm_flu_{}.out'.format(i+1, i+1)
        input_stream = open(amber_outfile, 'r')
        find_excited_energies(input_stream, output_stream, state_range)
    output_stream.close()
    average_energies_time = open('nasqm_flu_energy_time.txt', 'w')
    data = np.loadtxt('nasqm_flu_energies.txt')
    subprocess.run(['rm', 'nasqm_flu_energies.txt'])
    n_rows_per_trajectory = int(data.shape[0] / n_trajectories)
    for i in range(n_rows_per_trajectory):
        energy = np.average(data[i::n_rows_per_trajectory])
        average_energies_time.write(str(energy) + '\n')
