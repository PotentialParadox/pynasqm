import numpy as np
import sys

def load_data_from_files():
    return [np.loadtxt(fin) for fin in sys.argv[1:]]

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

def main():
    data = load_data_from_files()
    nstates = get_nstates(data)
    times = get_times(data)
    state_data = get_states(data)
    pops = pop_of_nstates(state_data,nstates)
    # print_population_chart(times, pops)
    print(string_population_chart(times,pops))

main()
