'''
Functions to parse amber output
'''
import re
import io
import numpy as np

def find_dipoles(file_stream):
    '''
    Return a numpy array of dipoles
    '''
    file_string = file_stream.read()
    dipoles = re.compile(r"MM DIPOLE\s*\-?\d+\.\d+\s+\-?\d+\.\d+\s+\-?\d+.\d+\s+(\-?\d+\.\d+)")
    search_results = re.findall(dipoles, file_string)
    dipoles = np.zeros(len(search_results))
    for i, value in enumerate(search_results):
        dipoles[i] = float(value)
    return dipoles


def read_nasqm_excited_states(input_stream, states):
    '''
    Return a tupple of of energies and strenghts
    read from an amber output file
    '''
    p_omega = re.compile(r'Frequencies \(eV\) and Oscillator')
    p_float = re.compile(r'-?\d+\.\d+E?-?\d*')
    energies = []
    strengths = []
    for line in input_stream:
        if re.search(p_omega, line):
            input_stream.readline()
            for state_value in range(max(states)):
                line2 = input_stream.readline()
                search_results = re.findall(p_float, line2)
                if state_value + 1 in states:
                    energies.append(search_results[0])
                    strengths.append(search_results[-1])
    return np.array(energies), np.array(strengths)


def create_spectra_string(output_stream, energies, strengths, states):
    '''
    Prints and returns a formated string using the appropriate inputs
    '''
    if not output_stream:
        output_stream = io.StringIO()
    n_steps = int(len(energies) / len(states))
    # NAESMD will run twice on the first iteration of a md simulation
    # we only want to count the second one. During singlepoint calculations
    # we don't need to worry about this.
    begin_step = 1 if n_steps > 1 else 0
    for step in range(begin_step, n_steps):
        for state in range(len(states)):
            index = len(states) * step + state
            output_stream.write("{: 24.14E}{: 24.14E}".format(float(energies[index]),
                                                              float(strengths[index])))
        output_stream.write('\n')
    return output_stream.getvalue()


def find_nasqm_excited_state(input_stream, output_stream=None, states=[1]):
    '''
    Write the firt n_states excited states energies and strengths to the output stream
    in eV
    '''
    energies, strengths = read_nasqm_excited_states(input_stream, states)
    return create_spectra_string(output_stream, energies, strengths, states)

def find_number_excited_states(input_stream):
    '''
    Finds the number of excited states propagated
    '''
    p_states = "Number of states to propagate"
    for line in input_stream:
        if re.search(p_states, line):
            n_states = re.findall(r"\d+", line)
            return int(n_states[0])


def find_excited_energies(input_stream, output_stream=None, states=[1]):
    '''
    Write the total energies of the excited state in eV
    '''
    is_io = None
    if output_stream is None:
        output_stream = io.StringIO()
        is_io = True
    p_energy = re.compile('Total energies of excited states')
    p_float = re.compile(r'-?\d+\.\d+E?\-?\+?\d*')
    for line in input_stream:
        if re.search(p_energy, line):
            for state_value in range(max(states)):
                line2 = input_stream.readline()
                search_results = re.findall(p_float, line2)
                if state_value + 1 in states:
                    output_stream.write("{: 24.14E}".format(float(search_results[0])) + '\n')
    if is_io:
        return output_stream.getvalue()
    return


def find_ground_energies(input_stream, output_stream=None):
    '''
    Write the total energies of the excited state in eV
    '''
    is_io = None
    if output_stream is None:
        output_stream = io.StringIO()
        is_io = True
    p_energy = re.compile('Total energy of the ground state')
    p_float = re.compile(r'-?\d+\.\d+E?\-?\+?\d*')
    for line in input_stream:
        if re.search(p_energy, line):
            line2 = input_stream.readline()
            search_results = re.findall(p_float, line2)
            output_stream.write("{: 24.14E}".format(float(search_results[0])) + '\n')
    if is_io:
        return output_stream.getvalue()
    return


def find_nasqm_transition_dipole(input_stream, output_stream=None):
    '''
    '''
    if not output_stream:
        output_stream = io.StringIO()
    p_energy_block = re.compile(r'Omega.*\n\s+\d\s+(-?\d+\.\d+E?\-?\d*\s*){5}')
    p_float = re.compile(r'-?\d+\.\d+E?-?\d*')
    search_results = re.findall(p_energy_block, input_stream)
    dipole_array = []
    for i in search_results:
        other_results = re.findall(p_float, i)
        dipole_array.append(float(other_results[0]))
    for i, dipole in enumerate(dipole_array):
        if i % 2 != 0:
            output_stream.write(str(dipole) + '\n')
    return output_stream.getvalue()

def find_total_energies(input_stream):
    '''
    Find the total energies in the amber output file
    and return a numpy array
    '''
    p_energies = re.compile(r"Etot\s*=\s+(\-?\d+\.\d+)")
    file_string = input_stream.read()
    search_results = re.findall(p_energies, file_string)
    energy_list = []
    for result in search_results:
        energy_list.append(float(result))
    return np.array(energy_list[:-2])

def find_mulliken(input_stream, state):
    '''
    This is designed for a single point calculation
    Returns the numpy array of the mulliken charges for a given state
    '''
    p_start = re.compile(r"\(0 - ground\)       {}".format(state))
    p_end = re.compile("Total Mulliken Charge")
    p_float = re.compile(r'-?\d+\.\d+E?\-?\+?\d*')
    list_charges = []
    for line in input_stream:
        if re.search(p_start, line):
            for line2 in input_stream:
                if re.search(p_end, line2):
                    break
                search_result = re.findall(p_float, line2)
                if not len(search_result) == 0:
                    list_charges.append(float(search_result[0]))
    n_atoms = int(len(list_charges) / 2)
    charges = np.array(list_charges[0:n_atoms])
    return charges

def find_molecular_orbitals(input_stream, output_stream=None):
    '''
    Returns a two row stream/string, the top row consisting of the occupied orbitals, and second,
    the virtual
    '''
    if not output_stream:
        output_stream = io.StringIO()
    p_occupied = re.compile("QMMM: Occupied MO Energies")
    p_virtual = re.compile("QMMM: Virtual MO Energies")
    p_float = re.compile(r'-?\d+\.\d+E?\-?\+?\d*')
    p_qmmm = re.compile("QMMM")
    for line in input_stream:
        line2 = ""
        if re.search(p_occupied, line):
            while not re.search(p_qmmm, line2):
                line2 = input_stream.readline()
                search_result = re.findall(p_float, line2)
                occupied_orbitals = np.array([float(i) for i in search_result])
                for orbital in occupied_orbitals:
                    output_stream.write("{: 16.8E}".format(orbital))
            output_stream.write("\n")
        if re.search(p_virtual, line2):
            line2 = ""
            while not re.search(p_qmmm, line2):
                line2 = input_stream.readline()
                search_result = re.findall(p_float, line2)
                occupied_orbitals = np.array([float(i) for i in search_result])
                for orbital in occupied_orbitals:
                    output_stream.write("{: 16.8E}".format(orbital))
            output_stream.write("\n")
    return output_stream.getvalue()


def find_scf_energies(input_stream, output_stream=None):
    '''
    Returns a stream/string with each line being an energy value
    '''
    if not output_stream:
        output_stream = io.StringIO()
    p_SCF_Energy = re.compile("QMMM: SCF Energy")
    p_float = re.compile(r'-?\d+\.\d+E?\-?\+?\d*')
    for line in input_stream:
        if re.search(p_SCF_Energy, line):
            search_result = re.findall(p_float, line)
            if len(search_result) > 0:
                output_stream.write(search_result[0] + "\n")
    return output_stream.getvalue()
