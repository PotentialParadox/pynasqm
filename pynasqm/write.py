"""
Functions that write outputs of the NASQM script
"""
import subprocess
import io
import numpy as np
from pynasqm.amberout import find_nasqm_excited_state, find_excited_energies


def numpy_to_specta_string(numpy_data):
    '''
    Converts a numpy array into the string used in spectra.input files
    '''
    string_output = ''
    for data in numpy_data:
        string_output += "{: 24.14E}{: 24.14E}".format(data[0], data[1]) + "\n"
    return string_output


def strip_timedelay(spectra_string, n_trajectories, time_step, time_delay):
    '''
    Remove the data from the equilibration time given by time_delay
    Time is in fs
    '''
    data = np.fromstring(spectra_string, sep=' ')
    n_rows = int(len(data) / 2)
    n_elements_traj = int(n_rows / n_trajectories)
    n_columns = 2
    data = data.reshape((n_rows, n_columns))
    n_rows_to_remove_traj = int(time_delay / time_step)
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
    return numpy_to_specta_string(data2)

def truncate_spectra(spectra_string, n_trajectories, time_step, time_delay):
    '''
    Truncate the spectra by a given time
    Time is in fs
    '''
    data = np.fromstring(spectra_string, sep=' ')
    n_rows = int(len(data) / 2)
    n_elements_traj = int(n_rows / n_trajectories)
    n_columns = 2
    data = data.reshape((n_rows, n_columns))
    n_rows_to_remove_traj = int(time_delay / time_step)
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
    return numpy_to_specta_string(data2)


def accumulate_flu_spectra(n_trajectories):
    """
    Create the spectra_flu.input file using the nasqm_flu_*.out files
    """
    n_states = 1
    output_stream = io.StringIO()
    for i in range(n_trajectories):
        amber_outfile = 'nasqm_flu_' + str(i+1) + ".out"
        input_stream = open(amber_outfile, 'r')
        find_nasqm_excited_state(input_stream, output_stream, states=[j for j in range(1, n_states+1)])
    output_string = output_stream.getvalue()
    output_stream.close()
    return output_string

def accumulate_abs_spectra(n_snapshots_gs, n_frames, n_states=20):
    '''
    Reads the data from the amber output files and writes the data to spectra_abs.input
    '''
    output_stream = io.StringIO()
    for traj in range(n_snapshots_gs):
        for frame in range(n_frames):
            amber_out = "nasqm_abs_{}_{}.out".format(traj+1, frame+1)
            input_stream = open(amber_out, 'r')
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
    open('spectra_abs.input', 'w').write(abs_string)

def write_spectra_flu_input(user_input):
    '''
    Writes the approriately formatted data to spectra_flu.input.
    Use hist_spectra_lifetime, and naesmd_spectra_plotter to get the spectra.
    '''
    fluor_string = accumulate_flu_spectra(n_trajectories=user_input.n_snapshots_ex)
    stripped_fl_string = strip_timedelay(fluor_string, user_input.n_snapshots_ex,
                                         user_input.time_step,
                                         user_input.fluorescence_time_delay)
    stripped_fl_string = truncate_spectra(fluor_string, user_input.n_snapshots_ex,
                                          user_input.time_step,
                                          user_input.fluorescence_time_truncation)
    open('spectra_flu.input', 'w').write(stripped_fl_string)


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
        amber_outfile = 'nasqm_flu_' + str(i+1) + ".out"
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
