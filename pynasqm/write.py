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
    print("Stripping time delay of {} from {} trajectories".format(time_delay, n_trajectories))
    row1 = spectra_string.split('\n', 1)[0]
    row1_data = np.fromstring(row1, sep=" ")
    n_columns = len(row1_data)
    data = np.fromstring(spectra_string, sep=" ")
    n_rows = int(len(data) / n_columns)
    n_elements_traj = int(n_rows / n_trajectories)
    data = data.reshape((n_rows, n_columns))
    print("Timestep: {}".format(time_step))
    print("ntpr: {}".format(ntpr))
    n_rows_to_remove_traj = int(time_delay / (time_step*ntpr))
    print("Removing first {} rows from each trajectory".format(n_rows_to_remove_traj))
    n_rows_to_remove = n_rows_to_remove_traj * n_trajectories
    print("Removing {} rows total".format(n_rows_to_remove))
    n_rows_data2 = n_rows - n_rows_to_remove
    if n_rows_data2 < 0:
        raise ValueError('Time delay greater than the runtime.\n'\
                         'N_Trajs: {}\n'\
                         'time_step: {}\n'\
                         'time_delay: {}\n'\
                         'ntpr: {}\n'.format(n_trajectories, time_step, time_delay, ntpr))
    data2 = np.zeros((n_rows_data2, n_columns))
    data2_ri = 0
    for i, data_point in enumerate(data):
        if i % n_elements_traj >= n_rows_to_remove_traj:
            data2[data2_ri][:] = data_point[:]
            data2_ri += 1
    answer = pynasqm.utils.numpy_to_txt(data2, form="scientific")
    return answer

def spectra_string_to_numpy(spectra_string):
    '''
    Given the string of an spectra.input file return a numpy array [step][info]
    '''
    row1 = spectra_string.split('\n', 1)[0]
    row1_data = np.fromstring(row1, sep=" ")
    n_columns = len(row1_data)
    data = np.fromstring(spectra_string, sep=" ")
    n_rows = int(len(data) / n_columns)
    return data.reshape((n_rows, n_columns))

def front_removal(in_list, n, e):
    '''
    Given an one dimesional list composed of n sublists of the same length l, remove
    r elements from the front of each sublist and recocatenate
    '''
    l = int(len(in_list)/n)
    if l < e:
        raise ValueError('Asking to remove more elements than contained in each sublist')
    return [x for (i, x) in enumerate(in_list) if i % l >= e]

def back_removal(in_list, n, e):
    '''
    Given an one dimesional list composed of n sublists of the same length l, remove
    r elements from the back of each sublist and recocatenate
    '''
    l = int(len(in_list)/n)
    if l < e:
        raise ValueError('Asking to remove more elements than contained in each sublist')
    return [x for (i, x) in enumerate(in_list) if i % l < l-e]


def truncate_spectra(spectra_string, n_trajectories, time_step, time_delay, ntpr=1):
    '''
    Truncate the spectra by a given time
    Time is in fs
    '''
    data = spectra_string_to_numpy(spectra_string)
    n_rows_to_remove_traj = int(time_delay / (time_step*ntpr))
    data2 = np.array(back_removal(data, n_trajectories, n_rows_to_remove_traj))
    answer = pynasqm.utils.numpy_to_txt(data2, form="scientific")
    return answer

def restart_finished(amber_outfile):
    '''
    Checks to see if the amber output file finished without
    '''
    try:
        lines = open(amber_outfile, 'r').readlines()
        if any (["wallclock() was called" in l for l in lines[-5:]]):
            return True
        return False
    except FileNotFoundError:
        return False

def traj_finished(amber_outfiles):
    '''
    Checks to see if all amber restart files for a trajectory finishes
    '''
    return all(restart_finished(x) for x in amber_outfiles)

def print_failed(failed_trajs):
    if failed_trajs == []:
        return ""
    failed_string = "Trajectories: "
    for traj in failed_trajs:
        failed_string += "{} ".format(traj)
    failed_string += "failed and are being skipped in the calculation of spectra"
    print(failed_string)

def amber_outputs(suffix, traj_id, n_restarts):
    return ["{}/traj_{}/restart_{}/nasqm_{}_t{}_r{}.out".format(suffix, traj_id, r, suffix, traj_id, r)
            for r in range(n_restarts+1)]

def read_excited_states_from_amberouts(amb_outs, n_states, output_stream):
    for amber_outfile in amb_outs:
        print("finding excited states from {}".format(amber_outfile))
        find_nasqm_excited_state(amber_outfile, output_stream,
                                 states=[j for j in range(1, n_states+1)])

def create_spectra_inputs(suffix, n_trajectories, n_restarts, n_states):
    script = "suffix={}\n".format(suffix)
    script += "ntrajs={}\n".format(n_trajectories)
    script += "nrestarts={}\n".format(n_restarts)
    script += "nstates={}\n".format(n_states)
    script += "nlines=$((nstates+1))\n"
    script += "awklines=$((nstates+3))\n"\
            "mkdir -p ${suffix}_spectra\n"\
            "for ((traj=1;traj<=$ntrajs;++traj)) do\n"\
            "    fileout=${suffix}_spectra/traj_${traj}.out\n"\
            "    > $fileout\n"\
            "    for ((restart=0;restart<=$nrestarts;++restart)) do\n"\
            "        filename=${suffix}/traj_${traj}/restart_${restart}/nasqm_${suffix}_t${traj}_r${restart}.out\n"\
            "        if [ -f $filename ]; then\n"\
            "            grep -A $nlines 'Frequencies (eV) and Oscillator' $filename\\\n"\
            "                | awk -v nlines=\"$awklines\" 'BEGIN{ORS=\"    \"};\n"\
            "{\n"\
            "    if (NR%nlines >2)\n"\
            "    {\n"\
            "      printf \"%24.14E%24.14E\", $2, $6;\n"\
            "    }\n"\
            "    if (NR%nlines ==0)\n"\
            "    {\n"\
            "      printf \"\\n\";\n"\
            "    }\n"\
            "}END{printf \"\\n\"}' >> $fileout \n"\
            "        fi\n"\
            "    done\n"\
            "done\n"
    open('spectra.sh', 'w').write(script)
    subprocess.run("bash spectra.sh", shell=True)

def filter_completed(data):
    nlines = [len(d.splitlines()) for d in data]
    maxlines = max (nlines)
    failed = []
    completed = []
    for i, n in enumerate(nlines):
        if n == maxlines:
            completed.append(data[i])
        else:
            failed.append(i+1)
    return completed, failed

def accumulate_spectra(n_trajectories, n_states=10, suffix='flu', n_restarts=0):
    """
    Create the spectra_flu.input file using the nasqm_flu_*.out files
    """
    create_spectra_inputs(suffix, n_trajectories, n_restarts, n_states)
    omegas_and_strengths = [open("{}_spectra/traj_{}.out".format(suffix, traj), 'r').read()
                            for traj in range(1, n_trajectories+1)]
    completed, failed_jobs = filter_completed(omegas_and_strengths)
    print_failed(failed_jobs)
    spectra_input = "".join(completed)
    return spectra_input, len(failed_jobs)

def write_spectra_abs_input(user_input):
    '''
    Writes the approriately formatted data to spectra_abs.input.
    Use hist_spectra_lifetime, and naesmd_spectra_plotter to get the spectra.
    '''
    abs_string, nfailed = accumulate_spectra(user_input.n_snapshots_gs,
                                            user_input.n_abs_exc,
                                            suffix='abs',
                                            n_restarts=user_input.n_abs_runs-1)
    time_step = user_input.time_step
    n_trajectories = user_input.n_snapshots_gs - nfailed
    abs_string = strip_timedelay(abs_string, n_trajectories, time_step,
                                 user_input.abs_time_delay, user_input.n_steps_to_print_abs)
    open('spectra_abs.input', 'w').write(abs_string)

def write_spectra_flu_input(user_input):
    '''
    Writes the approriately formatted data to spectra_flu.input.
    Use hist_spectra_lifetime, and naesmd_spectra_plotter to get the spectra.
    '''
    fluor_string, nfailed = accumulate_spectra(n_trajectories=user_input.n_snapshots_ex,
                                               n_states=user_input.n_exc_states_propagate_ex_param,
                                               suffix='flu',
                                               n_restarts=user_input.n_exc_runs-1)
    # The timestep needs to be adjusted for the number of frames skipped
    time_step = user_input.time_step
    n_trajectories = user_input.n_snapshots_ex - nfailed
    fluor_string = strip_timedelay(fluor_string, n_trajectories,
                                   time_step,
                                   user_input.fluorescence_time_delay,
                                   user_input.n_steps_to_print_exc)
    fluor_string = truncate_spectra(fluor_string, n_trajectories,
                                          time_step,
                                          user_input.fluorescence_time_truncation,
                                          user_input.n_steps_to_print_exc)
    open('spectra_flu.input', 'w').write(fluor_string)
    return n_trajectories

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
    filenames = ["flu/traj_{}/restart_0/coeff-n.out".format(x) for x in range(1, N+1)]
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
    print("Trajectories completed: {}".format(n_trajectories))
    n_rows_per_trajectory = int(data.shape[0] / n_trajectories)
    for i in range(n_rows_per_trajectory):
        omega = np.average(data[i::n_rows_per_trajectory, 0])
        average_omegas_time.write(str(omega) + '\n')
    average_omegas_time.close()

def test_accumulate_spectra():
    '''
    Test reading from one trajectory and one state for 0 restarts
    '''
    results, _ = accumulate_spectra(n_trajectories=1, n_states=1, suffix='abs')
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\

def test_accumulate_spectra1r():
    '''
    Test reading from one trajectory and one state for 1 restart
    '''
    results, _ = accumulate_spectra(n_trajectories=1, n_states=1, suffix='abs', n_restarts=1)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.83499537579971E+00    1.09712749914004E+00\n'\
                      '    2.83499537590646E+00    1.09712749898366E+00\n'\
                      '    2.84494863011054E+00    1.09014408841436E+00\n'\

def test_accumulate_spectra2s():
    '''
    Test reading from one trajectory and two states for 0 restarts
    Format line = omega1 dipole1 omega2 dipole2
    '''
    results, _ = accumulate_spectra(n_trajectories=1, n_states=2, suffix='abs', n_restarts=0)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00    3.11283401561629E+00    1.71114020911819E-03\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00    3.11283401572716E+00    1.71114021120587E-03\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00    3.13879515381299E+00    1.40558935033439E-03\n'\

def test_accumulate_spectra2t():
    '''
    Test reading from two trajectories and one state for 0 restarts
    '''
    results, _ = accumulate_spectra(n_trajectories=2, n_states=1, suffix='abs', n_restarts=0)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.79251675025885E+00    9.97596401377230E-01\n'\
                      '    2.79251675255889E+00    9.97596395053960E-01\n'\
                      '    2.77394015210517E+00    1.02463291276291E+00\n'\

def test_accumulate_spectra3t2rf():
    '''
    Test discarding a failed job that completes the zeroth restart but not the first restart
    '''
    results, _ = accumulate_spectra(n_trajectories=3, n_states=1, suffix='abs', n_restarts=1)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.83499537579971E+00    1.09712749914004E+00\n'\
                      '    2.83499537590646E+00    1.09712749898366E+00\n'\
                      '    2.84494863011054E+00    1.09014408841436E+00\n'\
                      '    2.79251675025885E+00    9.97596401377230E-01\n'\
                      '    2.79251675255889E+00    9.97596395053960E-01\n'\
                      '    2.77394015210517E+00    1.02463291276291E+00\n'\
                      '    2.76745094266644E+00    1.08681417088910E+00\n'\
                      '    2.76745094348021E+00    1.08681416841911E+00\n'\
                      '    2.75412095067397E+00    1.11226755671165E+00\n'\

def test_as_missing_file():
    '''
    For accumulate spectra, make sure it can discard trajectories that don't start all their restarts
    '''
    results, _ = accumulate_spectra(n_trajectories=4, n_states=1, suffix='abs', n_restarts=1)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.83499537579971E+00    1.09712749914004E+00\n'\
                      '    2.83499537590646E+00    1.09712749898366E+00\n'\
                      '    2.84494863011054E+00    1.09014408841436E+00\n'\
                      '    2.79251675025885E+00    9.97596401377230E-01\n'\
                      '    2.79251675255889E+00    9.97596395053960E-01\n'\
                      '    2.77394015210517E+00    1.02463291276291E+00\n'\
                      '    2.76745094266644E+00    1.08681417088910E+00\n'\
                      '    2.76745094348021E+00    1.08681416841911E+00\n'\
                      '    2.75412095067397E+00    1.11226755671165E+00\n'
