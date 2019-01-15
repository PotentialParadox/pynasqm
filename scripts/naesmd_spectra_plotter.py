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
parser.add_argument("--inputfile", "-i", help="The input file", default=None)
parser.add_argument("--comparison", "-c",
                    help="Are you comparing spectra?",
                    default="False")
parser.add_argument("--x_units", "-x", help="0-Ev or 1-nm", default=1, type=int)
parser.add_argument("--range", "-r", help="Provide two numbers,"\
                    "the minimum and maximum values in the units you prefer",
                    default=[0.0, 100.0], nargs="+", type=float)
args = parser.parse_args()


args.comparison = pynasqm.utils.str2bool(args.comparison)

color_code = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'b', 'g', (0.1, 0.2, 0.5)]

data = np.loadtxt(args.inputfile)

state_intensity_index_start = 2
state_intensity_index_end = 2 + args.number_states
x = data[:, args.x_units]
ys = data[:, state_intensity_index_start:state_intensity_index_end]

if args.comparison:
    for i in range(len(ys[0,:])):
        ys[:,i] = ys[:,i] / max(ys[:,i])
else:
    ys = ys / np.max(ys)

def filter_range(xin, yin, my_range):
    y_fitered = []
    x_filtered = []
    for x_temp, y_temp in zip(xin, yin):
        if my_range[0] <= x_temp <= my_range[1]:
            y_fitered.append(y_temp)
            x_filtered.append(x_temp)
    return (np.array(x_filtered), np.array(y_fitered))

(x, ys) = filter_range(x, ys, args.range)

for i in range(args.number_states):
    y = ys[:, i]
    color = color_code[i]
    # label = 'S' + str(i+1)
    label = args.labels[i]
    plt.plot(x, y, color=color, label=label)

if args.x_units == 0:
    plt.xlabel('Energy, eV')
else:
    plt.xlabel('Wavelength, nm')

ylabel = 'Intensity'

plt.ylabel(ylabel)
plt.title(args.title)
plt.legend(loc=2)
plt.yticks([])
plt.ylim((0,2))
plt.savefig(args.inputfile[:-4] + '.png')
plt.show()

