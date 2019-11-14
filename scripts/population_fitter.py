'''
Fits time constants by solving
-S5*k1                       = dS5
+S5*k1 -S4*k2                = dS4
       +S4*k2 -S3*k3         = dS3
              +S3*k3 -S2*k4  = dS2
                     +S2*k4  = dS1
which is a linear equation of the form
Ax=dx
we solve this using gradient decent
A'Ax = A'dx
x = (A'A)^{-1}A'dx
'''

import sys
import numpy as np

def load_data_from_file():
    return np.loadtxt(sys.argv[1])

def get_times(data):
    return data[:,0]

def get_states(data):
    return data[:,1:]

def get_timestep(times):
    return times[1] - times[0]

def generate_A_from_line(line):
    return np.array([
        [-line[4],        0,       0,         0],
        [ line[4], -line[3],       0,         0],
        [       0,  line[3], -line[2],        0],
        [0       ,        0,  line[2], -line[1]],
        [0       ,        0,        0,  line[1]]
    ])

def generate_A_from_states(states):
    A = generate_A_from_line(states[0])
    for line in states[1:-1]:
        B = generate_A_from_line(line)
        A = np.concatenate((A,B), axis=0)
    return A

def generate_ds_from_2lines(line1, line2):
    return np.flip(line2-line1) # Skip state 1

def generate_ds_from_states(dt, states):
    ds = generate_ds_from_2lines(states[0], states[1])
    for line1, line2 in zip(states[1:], states[2:]):
        b = generate_ds_from_2lines(line1, line2)
        ds = np.concatenate((ds,b), axis=0)
    return ds/dt

def solve_for_x(A, ds):
    A_squared = np.dot(A.T, A)
    A_squared_inv = np.linalg.inv(A_squared)
    full_operator = np.dot(A_squared_inv, A.T)
    return np.dot(full_operator, ds)

def calculate_time_constants(times, states):
    dt = get_timestep(times)
    A = generate_A_from_states(states)
    ds = generate_ds_from_states(dt, states)
    return solve_for_x(A, ds)

def main():
    data = load_data_from_file()
    times = get_times(data)
    states = get_states(data)
    print(calculate_time_constants(times, states))

main()
