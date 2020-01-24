'''
Given a list of coeff-n.out files returns a population chart
t | P(S1) | P(S2) | ... | P(Sn) |
'''
import numpy as np
import sys
import argparse
import functools

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pulsepump", help="simulating a pulse pump experiment", action="store_true")
    parser.add_argument("--files", "-l", help="coeff-n.out files", nargs="+")
    return parser.parse_args()

def filter_completed(data):
    max_length = max([len(d) for d in data])
    return [d for d in data if len(d) == max_length]

def load_data_from_files(files):
    return filter_completed([np.loadtxt(fin) for fin in files])

def get_nstates(data):
    ncols_not_coefficients=3
    return data[0].shape[1] - ncols_not_coefficients

def get_times(data):
    return data[0][:,1]

def get_states(data):
    return [d[:,0] for d in data]

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

def s1_sm(state, sm):
    return (int(state==1), int(state==sm))

def sum_two_list_of_pairs(s1_sm_as, s1_sm_bs):
    return tuple((s1_sm_a[0]+s1_sm_b[0], s1_sm_a[1]+s1_sm_b[1])
                 for s1_sm_a, s1_sm_b in zip(s1_sm_as, s1_sm_bs))


def trajectory_s1_sm(states):
    sm = states[0]
    return tuple(s1_sm(frame_state, sm) for frame_state in states)

def get_s1pop_smpops(state_data):
    return tuple(trajectory_s1_sm(traj) for traj in state_data)

def get_s1pop_smpop_sum(state_data):
    return functools.reduce(sum_two_list_of_pairs, get_s1pop_smpops(state_data))

def get_pulse_pump_pops(state_data):
    ntrajs = len(state_data)
    return tuple((frame[0]/ntrajs,frame[1]/ntrajs) for frame in get_s1pop_smpop_sum(state_data))

def string_list_of_pairs(pairs):
    return_value = ""
    for pair in pairs:
        return_value += "{:8.4f}{:8.4f}\n".format(pair[0], pair[1])
    return return_value

def main():
    args = parser()
    data = load_data_from_files(args.files)
    nstates = get_nstates(data)
    times = get_times(data)
    state_data = get_states(data)
    if args.pulsepump:
        print(string_list_of_pairs(get_pulse_pump_pops(state_data)))
    else:
        pops = pop_of_nstates(state_data,nstates)
        print(string_population_chart(times,pops))

main()
