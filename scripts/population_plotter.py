'''
Given a list of coeff-n.out files returns a population chart
t | P(S1) | P(S2) | ... | P(Sn) |
'''
import numpy as np
import sys
from os import path
import argparse
import functools
import itertools
from collections import namedtuple

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pulsepump", help="simulating a pulse pump experiment", action="store_true")
    parser.add_argument("--files", "-l", help="coeff-n.out files", nargs="+")
    parser.add_argument("--muab_files", help="the muab files whose energies"\
                        " and oscillators strengths will be used to filter", nargs="+")
    parser.add_argument("--min_energy", help="minimum energy differece (ev) from ground state for state S_m", type=float)
    parser.add_argument("--max_energy", help="maximum energy differece (ev) from ground state for state S_m", type=float)
    parser.add_argument("--min_strength", help="minimum oscillator from S1 for state S_m", type=float)
    return parser.parse_args()

def main():
    args = parser()
    coeff_files=split_files(args.files)
    muab_files=split_files(args.muab_files)
    data = load_data_from_files(coeff_files, muab_files)
    datac, datam = itertools.tee(data)
    coeff_data = (d.coeff for d in datac)
    coeff_data1, coeff_data2 = itertools.tee(coeff_data)
    muab_data = (d.muab for d in datam)
    state_data = get_states(coeff_data1)
    if args.pulsepump:
      Restraints = namedtuple('Restraints', 'min_energy, max_energy, min_strength')
      restraints = Restraints(args.min_energy, args.max_energy, args.min_strength)
      state_data = filter_pump_pulse(state_data, muab_data, restraints)
    first_coeff = next(coeff_data2)
    nstates = get_nstates(first_coeff)
    times = get_times(first_coeff)
    if args.pulsepump:
        print(string_list_of_pairs(times, get_pulse_pump_pops(state_data, nstates)))
    else:
        pops = pop_of_nstates(state_data,nstates)
        print(string_population_chart(times,pops))

def split_files(infilenames):
    outfilenames = None
    if infilenames:
        if len(infilenames) == 1:
            return infilenames[0].split()
    return infilenames

def load_data_from_files(files, muab_files):
    DataFiles = namedtuple('DataFiles', 'coeff, muab')
    if muab_files:
        return filter_completed(DataFiles(read_coeff(fin), read_muab(muab)) for fin, muab in zip(files, muab_files))
    return filter_completed([DataFiles(read_coeff(fin), None) for fin in files])

def filter_completed(data):
    (data1, data2) = itertools.tee(data)
    max_length = max([len(d[0]) for d in data1])
    return (d for d in data2 if len(d[0]) == max_length)

def read_coeff(coeff_file):
    if not path.exists(coeff_file):
        return np.array([])
    return np.loadtxt(coeff_file)

def read_muab(muab_file):
    if not path.exists(muab_file):
        return []
    muab_data = np.loadtxt(muab_file)
    return [muab_line(line) for line in muab_data]

def muab_line(line):
    MuabTuple = namedtuple('MuabTuple', 'init_state, fin_state, energy, x, y, z, strength')
    return MuabTuple(line[0], line[1], line[2], line[3], line[4], line[5], line[6])

def get_states(data):
    return (d[:,0] for d in data)

def filter_pump_pulse(state_data, muab_data, restraints):
    def sm_index(states):
        sm = states[0]
        return int(sm-1)
    return [states for (states, muab) in zip(state_data, muab_data)
            if satisfies_pulse_pump(restraints, muab[sm_index(states)])]

def satisfies_pulse_pump(restraints, muab_for_sm):
    return is_atleast(restraints.min_energy, muab_for_sm.energy) \
        and is_atmost(restraints.max_energy, muab_for_sm.energy) \
        and is_atleast(restraints.min_strength, muab_for_sm.strength)

def is_atleast(min_value, test):
    if min_value is None:
        return True
    return test >= min_value

def is_atmost(max_value, test):
    if max_value is None:
        return True
    return test >= max_value

def get_nstates(data):
    ncols_not_coefficients=3
    return data.shape[1] - ncols_not_coefficients

def get_times(data):
    return data[:,1]

def string_list_of_pairs(times, pairs):
    return_value = ""
    for time, pair in zip(times, pairs):
        return_value += "{:8.4f}{:8.4f}{:8.4f}{:8.4f}\n".format(time, pair[0], pair[1], pair[2])
    return return_value

def get_pulse_pump_pops(state_data, nstates):
    '''
    Returns a tuple with each element being (pop of s_1, pop of s_m)
    '''
    ntrajs = len(state_data)
    return tuple((frame[0]/ntrajs,frame[1]/ntrajs,frame[2]/ntrajs) for frame in get_sm_s1tosn_pop_sum(state_data, nstates))

def isstate(data, state):
    return (data == state).astype(int)

def pop_of_state(state_data, state):
    return np.sum(np.array([isstate(d, state) for d in state_data]), axis=0) / len(state_data)

def pop_of_nstates(state_data, nstates):
    return [pop_of_state(state_data,n) for n in range(1,nstates+1)]

def string_population_chart(times,pops):
    return_string = ""
    for i, time in enumerate(times):
        return_string +=  "{:10.5f}{}\n".format(time, string_population_at_frame(pops,i))
    return return_string

def string_population_at_frame(pops,frame):
    return "".join(["{:10.5f}".format(pop[frame]) for pop in pops])

def get_sm_s1tosn_pop_sum(state_data, nstates):
    '''
    Returns a tuple with each element being (number of s_m, number of s_1,..., number of s_n)
    '''
    return functools.reduce(sum_two_list_of_tuples, get_sm_s1tosn_pops(state_data, nstates))

def sum_two_list_of_tuples(pop_as, pop_bs):
    element_sum = lambda xs, ys : tuple([x+y for x,y in zip(xs,ys)])
    return tuple(element_sum(a,b)
                 for a, b in zip(pop_as, pop_bs))

def get_sm_s1tosn_pops(state_data, nstates):
    '''
    Returns a tuple where each element is a nested tuple where each element represents a frame
    (is_Sm, is_S1, ..., is_Sn)
    '''
    return tuple(trajectory_sm_s1tosn(traj, nstates) for traj in state_data)

def trajectory_sm_s1tosn(states, nstates):
    '''
    Returns a tuple where each element represents a frames condition
    (is_S1, is_Sm)
    '''
    sm = states[0]
    return tuple(sm_s1tosn(frame_state, sm, nstates) for frame_state in states)

def sm_s1tosn(state, sm, nstates):
    state_counts = [int(state==s) for s in range(1,nstates+1)]
    return tuple([int(state==sm)] + state_counts)

main()
