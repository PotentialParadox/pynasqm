import argparse
import numpy as np
import matplotlib.pyplot as plt
import pynasqm.utils
from scipy.interpolate import spline

parser = argparse.ArgumentParser()
parser.add_argument("--title", help="The title of the graph", default="Title")
parser.add_argument("--number_states", help="The number of states you want to include.",
                    default=1, type=int)
parser.add_argument("--labels", "-l", help="labels of the data", default=[1], nargs="+")
parser.add_argument("--inputfile", "-i", help="The input file", default="spectra_flu.output")
parser.add_argument("--absorbance", "-a",
                    help="Is the file absorbance (True) or Fluorescence (False)",
                    default="False")
parser.add_argument("--x_units", "-x", help="0-Ev or 1-nm", default=1, type=int)
args = parser.parse_args()

color_code = ['r', 'g', 'b', 'y', 'm']

data = np.loadtxt(args.inputfile)

state_intensity_index_start = 2
state_intensity_index_end = 2 + args.number_states
x = data[:, args.x_units]
ys = data[:, state_intensity_index_start:state_intensity_index_end]

for i in range(args.number_states):
    y = ys[:, i]
    color = color_code[i]
    # label = 'S' + str(i+1)
    label = args.labels[i]
    plt.plot(x, y, color=color, label=label)

if args.x_units == 0:
    plt.xlabel('Energy, eV')
    plt.gca().invert_xaxis()
else:
    plt.xlabel('Wavelength, nm')

if my_utils.str2bool(args.absorbance):
    ylabel = 'Normalized Absorbance'
else:
    ylabel = 'Normalized Fluorescence'

plt.ylabel(ylabel)
plt.title(args.title)
plt.legend(loc=2)
plt.savefig(args.inputfile[:-7] + '.png')
plt.show()


