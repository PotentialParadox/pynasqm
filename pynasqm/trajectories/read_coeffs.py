import re
import numpy as np

def read_coeffs(filename):
    coeffs = []
    p_coeffs = re.compile(r'-?\d+\.\d+E?-?\d*\s+-?\d+\.\d+E?-?\d*')
    with open(filename, 'r') as filein:
        for line in filein:
            if re.search(p_coeffs, line):
                coeffs.append([float(x) for x in line.split()])
    return np.array(coeffs)
