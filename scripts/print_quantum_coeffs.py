import argparse
import numpy as np
from pynasqm.coeffreader import get_times, get_coeffs, graph_coeffs

def main(filename, title):
    filestring = open(filename, 'r').read()
    times = None
    coeffs = None
    if not args.average:
        times = get_times(filestring)
        coeffs = get_coeffs(filestring)
    else:
        data = np.loadtxt(args.filename)
        times = data[:,0]
        coeffs = data[:,1:]
    graph_coeffs(times, coeffs, title)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", default="coefficient.out")
parser.add_argument("-t", "--title", default="State Coefficients")
parser.add_argument("-a", "--average", help="Using average ceoff values", type=bool, default=False)
args = parser.parse_args()

main(args.filename, args.title)
