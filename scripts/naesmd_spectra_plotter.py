import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pynasqm.utils
from scipy.interpolate import spline

parser = argparse.ArgumentParser()
parser.add_argument("--title", help="The title of the graph", default="Title")
parser.add_argument("--number_states", help="The number of states you want to include.",
                    default=1, type=int)
parser.add_argument("--labels", "-l", help="labels of the data", default=[1,2,3,4,5,6,7,8,9,10,11,
                                                                          12,13,14,15,16,17,18,19], nargs="+")
parser.add_argument("--ylabel", help="labels for you y axis", default="")
parser.add_argument("--inputfile", "-i", help="The input file", default=None)
parser.add_argument("--outputfile", "-o", help="The output file", default=None)
parser.add_argument("--letter", help="The letter in the paper", default="")
parser.add_argument("--comparison", "-c",
                    help="Are you comparing spectra?",
                    default="False")
parser.add_argument("--x_units", "-x", help="0-Ev or 1-nm", default=0, type=int)
parser.add_argument("--range", "-r", help="Provide two numbers,"\
                    "the minimum and maximum values in the units you prefer",
                    default=[0.0, 100.0], nargs="+", type=float)
args = parser.parse_args()


args.comparison = pynasqm.utils.str2bool(args.comparison)

data = np.loadtxt(args.inputfile)

state_intensity_index_start = 2
state_intensity_index_end = 2 + args.number_states
X = data[:, args.x_units]
Ys = data[:, state_intensity_index_start:state_intensity_index_end]

def plotter(x, ys):
    ys = normalize_individuals(ys) if args.comparison else normalize_set(ys)
    (x, ys) = filter_range(x, ys, args.range)

    sns.set()
    sns.set_style("white")
    sns.set_style("ticks")

    fig, ax = plt.subplots()
    for i in range(args.number_states):
        y = ys[:, i]
        label = args.labels[i]
        ax.plot(x, y, label=label)

    xlabel = "Energy (eV)" if args.x_units == 0 else "Wavelength (nm)"
    ax.set_xlabel(xlabel)
    ax.set_ylabel(args.ylabel)
    ax.legend(loc=1)
    ax.axes.get_yaxis().set_ticks([])
    ax.set_ylim((0, 1.5))
    ax.text(-0.05, 0.95, args.letter, transform=ax.transAxes,
            fontsize=17, fontweight='bold', va='top')
    fig.savefig(args.outputfile)
    plt.show()


def normalize_individuals(ys):
    '''
    All spectra maximum values will equal
    '''
    return np.divide(ys, ys.max(0))

def normalize_set(ys):
    '''
    Spectra will keep relative magnitudes
    '''
    return np.divide(ys, np.max(ys))


def filter_range(xin, yin, my_range):
    y_fitered = []
    x_filtered = []
    for x_temp, y_temp in zip(xin, yin):
        if my_range[0] <= x_temp <= my_range[1]:
            y_fitered.append(y_temp)
            x_filtered.append(x_temp)
    return (np.array(x_filtered), np.array(y_fitered))


plotter(X, Ys)


