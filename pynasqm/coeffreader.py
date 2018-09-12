import re
import numpy as np
import matplotlib.pyplot as plt

def get_coeffs(filename):
    '''
    returns [timestep][state coeff]
    '''
    data = np.loadtxt(filename)
    return list(data[:,2:-1])

def get_times(filename):
    # find time =         (timevalue)
    data = np.loadtxt(filename)
    return list(data[:,1])

def graph_coeffs(times, coeffs, title):
    x = times
    n_states = len(coeffs[0])
    for state in range(n_states):
        y = [coeff_block[state] for coeff_block in coeffs]
        plt.plot(x, y, label="state {}".format(state+1))
    plt.legend()
    plt.xlabel("Time (fs)")
    plt.title(title)
    plt.show()
